"""
Load Boss Assistant input from MYOB (AccountRight / Business API).
Client connects MYOB once (OAuth); we store refresh_token and pull P&L each run.
"""
import json
import os
import urllib.request
from datetime import date, timedelta
from typing import Any, Optional

from input_model import BossInput, ValidationError

MYOB_TOKEN_URL = "https://secure.myob.com/oauth2/v1/authorize"
MYOB_API_BASE = "https://api.myob.com/accountright/"


def _get_access_token(
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> str:
    """Exchange refresh_token for a new access_token."""
    data = (
        f"client_id={urllib.parse.quote(client_id)}"
        f"&client_secret={urllib.parse.quote(client_secret)}"
        f"&refresh_token={urllib.parse.quote(refresh_token)}"
        "&grant_type=refresh_token"
    ).encode("utf-8")
    req = urllib.request.Request(
        MYOB_TOKEN_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    return out["access_token"]


def _fetch_pl_report(
    cf_uri: str,
    access_token: str,
    api_key: str,
    start_date: date,
    end_date: date,
    reporting_basis: str = "Accrual",
    year_end_adjust: str = "No",
) -> Any:
    """GET ProfitAndLossSummary for the date range. Returns raw JSON."""
    path = (
        f"{cf_uri}/Report/ProfitAndLossSummary"
        f"?StartDate={start_date.isoformat()}"
        f"&EndDate={end_date.isoformat()}"
        f"&ReportingBasis={reporting_basis}"
        f"&YearEndAdjust={year_end_adjust}"
    )
    url = MYOB_API_BASE.rstrip("/") + "/" + path.lstrip("/")
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "x-myobapi-key": api_key,
            "x-myobapi-version": "v2",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _sum_revenue_from_pl_response(data: Any) -> float:
    """
    Extract total revenue/income from MYOB P&L response.
    Handles common shapes: TotalIncome, rows with Amount, TaxCodeBreakdown totals.
    """
    if isinstance(data, (int, float)):
        return float(data)
    if isinstance(data, dict):
        for key in ("TotalIncome", "TotalRevenue", "Revenue", "Income", "Total"):
            if key in data and isinstance(data[key], (int, float)):
                return float(data[key])
        total = 0.0
        for key in ("TaxCodeBreakdown", "Rows", "Items", "Accounts"):
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    total += _sum_revenue_from_pl_response(item)
        if total != 0:
            return total
        for v in data.values():
            total += _sum_revenue_from_pl_response(v)
        return total
    if isinstance(data, list):
        return sum(_sum_revenue_from_pl_response(item) for item in data)
    return 0.0


def _sum_costs_from_pl_response(data: Any) -> float:
    """
    Extract total costs/expenses from MYOB P&L response.
    Handles TotalExpenses, TotalCostOfSales, CostOfSales, Expenses, etc.
    """
    if isinstance(data, (int, float)):
        return float(data)
    if isinstance(data, dict):
        for key in (
            "TotalExpenses",
            "TotalCostOfSales",
            "CostOfSales",
            "Expenses",
            "TotalCost",
            "TotalCosts",
        ):
            if key in data and isinstance(data[key], (int, float)):
                return float(data[key])
        total = 0.0
        for key in ("TaxCodeBreakdown", "Rows", "Items", "Accounts"):
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    total += _sum_costs_from_pl_response(item)
        if total != 0:
            return total
        for v in data.values():
            total += _sum_costs_from_pl_response(v)
        return total
    if isinstance(data, list):
        return sum(_sum_costs_from_pl_response(item) for item in data)
    return 0.0


def load_from_myob(
    cf_uri: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
    api_key: str,
    company_name: Optional[str] = None,
    budget_this_month: float = 0.0,
    jobs_this_month: int = 0,
    jobs_last_month: int = 0,
    reporting_basis: str = "Accrual",
    year_end_adjust: str = "No",
) -> BossInput:
    """
    Pull this month and last month revenue from MYOB P&L; build BossInput.
    Jobs and budget are not in P&L by default — pass them in or leave 0.
    """
    access_token = _get_access_token(refresh_token, client_id, client_secret)
    today = date.today()
    # This month
    start_this = today.replace(day=1)
    end_this = today
    # Last month
    # Last month: first day to last day
    if today.month == 1:
        start_last = today.replace(year=today.year - 1, month=12, day=1)
        end_last = today.replace(year=today.year - 1, month=12, day=31)
    else:
        start_last = today.replace(month=today.month - 1, day=1)
        end_last = start_this - timedelta(days=1)
    pl_this = _fetch_pl_report(cf_uri, access_token, api_key, start_this, end_this, reporting_basis, year_end_adjust)
    pl_last = _fetch_pl_report(cf_uri, access_token, api_key, start_last, end_last, reporting_basis, year_end_adjust)
    revenue_this = _sum_revenue_from_pl_response(pl_this)
    revenue_last = _sum_revenue_from_pl_response(pl_last)
    return BossInput.from_dict({
        "revenue_this_month": round(revenue_this, 2),
        "revenue_last_month": round(revenue_last, 2),
        "budget_this_month": budget_this_month,
        "jobs_this_month": jobs_this_month,
        "jobs_last_month": jobs_last_month,
        "company_name": company_name,
    })


def load_from_myob_config(config: dict) -> BossInput:
    """
    Load from MYOB using env vars and config.
    Config: myob_cf_uri, myob_refresh_token_env, myob_client_id_env, myob_client_secret_env, myob_api_key_env,
            company_name, myob_budget (optional), myob_jobs_this, myob_jobs_last (optional),
            myob_reporting_basis, myob_year_end_adjust.
    Env (from *_env keys): refresh_token, client_id, client_secret, api_key.
    """
    cf_uri = config.get("myob_cf_uri") or os.environ.get("MYOB_CF_URI")
    if not cf_uri:
        raise ValueError("myob_cf_uri or MYOB_CF_URI required")
    refresh_env = config.get("myob_refresh_token_env") or "MYOB_REFRESH_TOKEN"
    client_id_env = config.get("myob_client_id_env") or "MYOB_CLIENT_ID"
    client_secret_env = config.get("myob_client_secret_env") or "MYOB_CLIENT_SECRET"
    api_key_env = config.get("myob_api_key_env") or "MYOB_API_KEY"
    refresh_token = os.environ.get(refresh_env)
    client_id = os.environ.get(client_id_env)
    client_secret = os.environ.get(client_secret_env)
    api_key = os.environ.get(api_key_env)
    if not all([refresh_token, client_id, client_secret, api_key]):
        raise ValueError(
            f"Set env vars: {refresh_env}, {client_id_env}, {client_secret_env}, {api_key_env}"
        )
    return load_from_myob(
        cf_uri=cf_uri.strip(),
        refresh_token=refresh_token.strip(),
        client_id=client_id.strip(),
        client_secret=client_secret.strip(),
        api_key=api_key.strip(),
        company_name=config.get("company_name"),
        budget_this_month=float(config.get("myob_budget") or 0),
        jobs_this_month=int(config.get("myob_jobs_this") or 0),
        jobs_last_month=int(config.get("myob_jobs_last") or 0),
        reporting_basis=config.get("myob_reporting_basis") or "Accrual",
        year_end_adjust=config.get("myob_year_end_adjust") or "No",
    )

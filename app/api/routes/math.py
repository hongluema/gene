from fractions import Fraction

from fastapi import APIRouter, HTTPException, status

from app.schemas.math import EYResult


router = APIRouter()


@router.get("/ey/{n}", response_model=EYResult)
def compute_ey(n: int):
    """
    已知集合 M = {1, 2, 3, ..., n}（n ∈ N*），从 M 中随机抽取一个数记为 X，
    再从 X, X+1, ..., n 中随机抽取一个数记为 Y，计算 E(Y)。

    推导：
      P(X=k) = 1/n
      E(Y|X=k) = (k + n) / 2
      E(Y) = Σ_{k=1}^{n} (1/n) * (k+n)/2
           = (1/2n) * [n(n+1)/2 + n²]
           = (3n+1) / 4
    """
    if n < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="n must be a positive integer (n ∈ N*)",
        )

    result = Fraction(3 * n + 1, 4)
    return EYResult(
        n=n,
        expected_value=float(result),
        fraction=f"{result.numerator}/{result.denominator}",
    )

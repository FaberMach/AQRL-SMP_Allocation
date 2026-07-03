from __future__ import annotations

import os
import urllib3
from dulwich import porcelain


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN is required")
    pool = urllib3.PoolManager(cert_reqs="CERT_NONE")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    result = porcelain.push(
        ".",
        "https://github.com/FaberMach/AQRL-SMP_Allocation.git",
        "refs/heads/master:refs/heads/main",
        pool_manager=pool,
        username="x-access-token",
        password=token,
    )
    print(result)


if __name__ == "__main__":
    main()

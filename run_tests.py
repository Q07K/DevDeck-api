#!/usr/bin/env python3
"""
테스트 실행 스크립트

이 스크립트는 다양한 옵션으로 테스트를 실행할 수 있습니다.
"""

import argparse
import subprocess
import sys


def run_tests(test_type=None, verbose=False, coverage=False, markers=None):
    """pytest를 이용해 테스트 실행"""

    cmd = ["uv", "run", "pytest"]

    # 테스트 타입에 따른 경로 설정
    if test_type == "auth":
        cmd.append("tests/test_auth_api.py")
    elif test_type == "posts":
        cmd.append("tests/test_posts_api.py")
    elif test_type == "users":
        cmd.append("tests/test_users_api.py")
    elif test_type == "blog":
        cmd.append("tests/test_blog_api.py")
    elif test_type == "database":
        cmd.append("tests/test_database.py")
    elif test_type == "api":
        cmd.append("tests/test_api_endpoints.py")
    elif test_type == "sqlalchemy":
        cmd.append("tests/test_sqlalchemy_structure.py")
    elif test_type == "main":
        cmd.append("tests/test_main.py")
    else:
        cmd.append("tests/")

    # 옵션 추가
    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])

    if markers:
        cmd.extend(["-m", markers])

    # 테스트 실행
    result = subprocess.run(cmd, capture_output=False, check=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="DevDeck API 테스트 실행")
    parser.add_argument(
        "type",
        nargs="?",
        choices=[
            "auth",
            "posts",
            "users",
            "blog",
            "database",
            "api",
            "sqlalchemy",
            "main",
            "all",
        ],
        default="all",
        help="실행할 테스트 타입",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="상세한 출력"
    )
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="커버리지 리포트 포함"
    )
    parser.add_argument("-m", "--markers", help="특정 마커로 테스트 필터링")

    args = parser.parse_args()

    print(f"🚀 DevDeck API 테스트 실행 - {args.type}")
    print("=" * 50)

    test_type = None if args.type == "all" else args.type

    exit_code = run_tests(
        test_type=test_type,
        verbose=args.verbose,
        coverage=args.coverage,
        markers=args.markers,
    )

    if exit_code == 0:
        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print(f"\n❌ 테스트가 실패했습니다. (종료 코드: {exit_code})")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

"""Command-line interface for Agentic Council."""

import argparse
import asyncio
import sys

from agentic_council import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic Council - Multi-agent business idea evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"agentic-council {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a business idea")
    eval_parser.add_argument("idea", help="The business idea to evaluate")
    eval_parser.add_argument(
        "--risk",
        choices=["conservative", "moderate", "aggressive"],
        default="moderate",
        help="Risk appetite level",
    )
    eval_parser.add_argument(
        "--time",
        type=int,
        default=900,
        help="Total time limit in seconds",
    )

    # Backtest command
    backtest_parser = subparsers.add_parser("backtest", help="Run historical backtests")
    backtest_parser.add_argument(
        "--test",
        help="Specific test ID to run",
    )
    backtest_parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests",
    )

    # Server command
    server_parser = subparsers.add_parser("server", help="Start the API server")
    server_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to",
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on",
    )

    # Dashboard command
    dash_parser = subparsers.add_parser("dashboard", help="Start the Streamlit dashboard")
    dash_parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port for dashboard",
    )

    args = parser.parse_args()

    if args.command == "evaluate":
        asyncio.run(run_evaluate(args))
    elif args.command == "backtest":
        asyncio.run(run_backtest(args))
    elif args.command == "server":
        run_server(args)
    elif args.command == "dashboard":
        run_dashboard(args)
    else:
        parser.print_help()


async def run_evaluate(args):
    """Run evaluation from CLI."""
    from agentic_council.orchestration.council import AgenticCouncil, CouncilConfig
    from agentic_council.orchestration.voting import RiskAppetite

    print(f"Evaluating: {args.idea[:50]}...")
    print(f"Risk appetite: {args.risk}")
    print(f"Time limit: {args.time}s")
    print("-" * 50)

    config = CouncilConfig(
        total_time_seconds=args.time,
        risk_appetite=RiskAppetite(args.risk),
    )

    council = AgenticCouncil(config=config)

    try:
        session = await council.evaluate(idea=args.idea)

        print("\n" + "=" * 50)
        print("EVALUATION COMPLETE")
        print("=" * 50)

        if session.final_consensus:
            consensus = session.final_consensus
            print(f"\nRecommendation: {consensus.recommendation.value.upper()}")
            print(f"Confidence: {consensus.confidence:.0%}")
            print(f"Weighted Score: {consensus.weighted_score:.1f}/10")

            print("\nKey Drivers:")
            for driver in consensus.key_drivers[:3]:
                print(f"  + {driver}")

            print("\nMajor Risks:")
            for risk in consensus.major_risks[:3]:
                print(f"  - {risk}")

            print(f"\nDuration: {session.duration_seconds:.1f}s")
        else:
            print("Evaluation incomplete")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


async def run_backtest(args):
    """Run backtests from CLI."""
    from agentic_council.orchestration.council import AgenticCouncil
    from agentic_council.evaluation.historical_tests import HistoricalTestRunner

    council = AgenticCouncil()
    runner = HistoricalTestRunner(council)

    print("Running historical backtests...")
    print("-" * 50)

    try:
        if args.test:
            results = [await runner.run_test(args.test, verbose=True)]
        elif args.all:
            results = await runner.run_all_tests(verbose=True)
        else:
            print("Available test cases:")
            for test_id in runner.list_test_cases():
                print(f"  - {test_id}")
            return

        stats = runner.get_aggregate_stats()
        print("\n" + "=" * 50)
        print("BACKTEST SUMMARY")
        print("=" * 50)
        print(f"Total tests: {stats['total_tests']}")
        print(f"Passed: {stats['passed']}")
        print(f"Failed: {stats['failed']}")
        print(f"Pass rate: {stats['pass_rate']:.0%}")
        print(f"Average accuracy: {stats['average_accuracy']:.0%}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_server(args):
    """Start the API server."""
    import uvicorn
    from agentic_council.api.server import app

    print(f"Starting API server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


def run_dashboard(args):
    """Start the Streamlit dashboard."""
    import subprocess
    import sys

    print(f"Starting dashboard on port {args.port}")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "agentic_council/dashboard/app.py",
        "--server.port", str(args.port),
        "--server.address", "0.0.0.0",
    ])


if __name__ == "__main__":
    main()

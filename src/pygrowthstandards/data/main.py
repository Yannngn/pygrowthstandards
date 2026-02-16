"""Entry point for running growth and development ETL pipelines."""

from pygrowthstandards.data.development.main import run_milestone_etl
from pygrowthstandards.data.growth.main import run_growth_etl


def _print_title(title: str) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    _print_title("PYGROWTHSTANDARDS DATA ETL")
    print("\nRunning growth reference ETL...")
    run_growth_etl()
    print("\nRunning development milestones ETL...")
    run_milestone_etl()
    print("\nAll ETL tasks complete.")


if __name__ == "__main__":
    main()

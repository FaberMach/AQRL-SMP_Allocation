from aqrl.core.scheduler import Scheduler


def test_scheduler_registers_and_runs_task() -> None:
    scheduler = Scheduler()
    calls: list[str] = []

    def build() -> str:
        calls.append("build")
        return "done"

    scheduler.register("build", build)

    assert scheduler.list() == ("build",)
    assert scheduler.run("build") == "done"
    assert calls == ["build"]


def test_scheduler_runs_all_tasks_in_order() -> None:
    scheduler = Scheduler()
    calls: list[str] = []

    def first() -> int:
        calls.append("first")
        return 1

    def second() -> int:
        calls.append("second")
        return 2

    scheduler.register("first", first)
    scheduler.register("second", second)

    results = scheduler.run_all()

    assert results == {"first": 1, "second": 2}
    assert calls == ["first", "second"]

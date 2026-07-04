from aqrl.core.events import Event, EventBus


def test_event_normalizes_and_copies_payloads() -> None:
    payload = {"symbol": "AAPL", "price": 101.25}
    metadata = {"channel": "feed"}

    event = Event(name=" market.tick ", payload=payload, source=" engine ", metadata=metadata)

    assert event.name == "market.tick"
    assert event.payload == payload
    assert event.payload is not payload
    assert event.metadata == metadata
    assert event.metadata is not metadata
    assert event.source == "engine"
    assert event.timestamp.tzinfo is not None


def test_event_bus_dispatches_synchronously_in_order() -> None:
    bus = EventBus()
    calls: list[str] = []
    seen: list[Event] = []

    def first_handler(event: Event) -> str:
        seen.append(event)
        calls.append("first")
        return "first-result"

    def second_handler(event: Event) -> str:
        calls.append("second")
        return "second-result"

    bus.subscribe("market.tick", first_handler)
    bus.subscribe("market.tick", second_handler)

    event = Event(name="market.tick", payload={"price": 100.5})
    results = bus.publish(event)

    assert calls == ["first", "second"]
    assert seen == [event]
    assert results == ["first-result", "second-result"]


def test_event_bus_unsubscribe_stops_dispatch() -> None:
    bus = EventBus()
    calls: list[str] = []

    def handler(event: Event) -> None:
        calls.append(event.name)

    bus.subscribe("market.tick", handler)
    assert bus.unsubscribe("market.tick", handler) is True
    assert bus.unsubscribe("market.tick", handler) is False

    bus.publish(Event(name="market.tick"))

    assert calls == []

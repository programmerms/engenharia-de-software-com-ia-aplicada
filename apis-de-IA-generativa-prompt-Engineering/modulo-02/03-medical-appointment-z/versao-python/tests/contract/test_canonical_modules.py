import inspect

from app import appointment_service, factory, llm_service, models, router, state


def test_canonical_modules_expose_the_documented_architecture() -> None:
    assert models.IntentExtraction.__name__ == "IntentExtraction"
    assert llm_service.OpenRouterMedicalLLM.__name__ == "OpenRouterMedicalLLM"
    assert state.GraphState is not None
    assert callable(router.route_medical)
    assert callable(factory.build_graph)
    assert appointment_service.AppointmentCatalog.__name__ == "AppointmentCatalog"


def test_canonical_public_symbols_have_didactic_documentation() -> None:
    public = (
        models.IntentExtraction,
        models.MessageGeneration,
        llm_service.OpenRouterMedicalLLM,
        llm_service.FakeMedicalLLM,
        appointment_service.AppointmentCatalog,
        router.route_medical,
        factory.build_graph,
        state.create_medical_state,
    )

    assert all(inspect.getdoc(symbol) for symbol in public)

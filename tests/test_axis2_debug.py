from axis2.builder import Axis2Builder
import pprint


def test_axis2_debug_dump(hydra_axis1, game_state):
    """
    Diagnostic test: prints the full Axis2Card structure so you can inspect it.
    Run with: pytest -s
    """

    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    print("\n=== AXIS 2 DEBUG DUMP ===")

    print("\nACTIONS:")
    for name, action in axis2.actions.items():
        print(f"  {name}: {action}")

    print("\nZONE PERMISSIONS:")
    pprint.pprint(axis2.zone_permissions.permissions)

    print("\nTRIGGERS:")
    for trig in axis2.triggers:
        print(f"  {trig}")

    print("\nGLOBAL RESTRICTIONS:")
    for r in axis2.global_restrictions:
        print(f"  {r}")

    print("\nLIMITS:")
    for l in axis2.limits:
        print(f"  {l}")

    print("\nVISIBILITY:")
    print(axis2.visibility_constraints)

    print("\n==========================")

    # Always assert something so pytest doesn't mark this as "no assertions"
    assert axis2 is not None
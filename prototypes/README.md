# API Design Prototypes

This directory contains prototype implementations for potential fluid API enhancements to PyGrowthStandards.

## Files

- `fluent_patient.py`: Enhanced Patient class with method chaining
- `patient_builder.py`: Builder pattern implementation for Patient construction
- `unified_api.py`: Facade pattern for simplified API access
- `usage_examples.py`: Comparison of different API styles

## Purpose

These prototypes demonstrate different API design patterns without modifying the core library. They serve as:

1. **Design exploration** - Test different patterns before implementation
2. **User feedback** - Gather community input on preferred approaches
3. **Documentation** - Show concrete examples of proposed changes
4. **Decision support** - Compare tradeoffs between patterns

## How to Use

These are standalone prototypes and won't run without the full library context. They're meant to be read and evaluated for design decisions, not executed directly.

To test concepts from these prototypes:
1. Review the code and usage patterns
2. Provide feedback via GitHub Issues or Discussions
3. Vote on preferred approaches
4. Suggest improvements or alternatives

## Status

**Current Status:** Research & Design Phase  
**Implementation:** Not yet integrated into main library  
**Feedback Welcome:** Yes, please share your thoughts!

## Next Steps

Based on the research document (`FLUID_API_RESEARCH.md`), the recommended implementation order is:

1. **Phase 1**: Method chaining in existing classes (fluent_patient.py)
2. **Phase 2**: Builder pattern (patient_builder.py)
3. **Phase 3**: Unified facade (unified_api.py)

See `FLUID_API_RESEARCH.md` for full details.

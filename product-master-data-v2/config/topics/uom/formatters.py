from typing import Dict, List 


class UOMReferenceFormatter:

    @staticmethod
    def format_code_to_variations(code_to_variations: Dict[str, List[str]]) -> str:

        lines = []
        lines.append("SYSTEM UNIT CODES AND THEIR INPUT VARIATIONS:")
        lines.append("(Always output the system code, even if input uses a variation)\n")
        
        for code in sorted(code_to_variations.keys()):
            variations = code_to_variations[code]
            variations_str = ', '.join(f"'{v}'" for v in variations)
            lines.append(f"{code}:")
            lines.append(f"  Input variations: {variations_str}")
            lines.append(f'  Output in JSON: "{code}"\n')
        
        return "\n".join(lines)
    
    # ==================================================================

    @staticmethod
    def format_unit_codes(unit_codes: List[str]) -> str:
        codes_str = ', '.join(sorted(unit_codes))
        return f"Valid system unit codes: {codes_str}"
    
    # ==================================================================
    
    @staticmethod
    def format_reference_data(code_to_variations: Dict[str, List[str]] = None,
                              unit_codes: List[str] = None) -> str:
        parts = []
        
        # Format code_to_variations (preferred)
        if code_to_variations:
            parts.append(UOMReferenceFormatter.format_code_to_variations(code_to_variations))
        
        # Format unit codes (fallback or additional info)
        if unit_codes and not code_to_variations:
            parts.append(UOMReferenceFormatter.format_unit_codes(unit_codes))
        
        return "\n\n".join(parts)
    
    # ==================================================================
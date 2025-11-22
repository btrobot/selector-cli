"""
Test Phase 2 lexer enhancements
"""
import sys
from pathlib import Path

parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.parser.lexer import Lexer, TokenType


def test_phase2_tokens():
    """Test Phase 2 token types"""
    print("="*60)
    print("Testing Phase 2 Lexer Enhancements")
    print("="*60)

    lexer = Lexer()

    # Test cases for Phase 2 features
    test_cases = [
        # Comparison operators
        ("where index > 5", "Comparison: greater than"),
        ("where index >= 10", "Comparison: greater than or equal"),
        ("where index < 20", "Comparison: less than"),
        ("where index <= 30", "Comparison: less than or equal"),

        # Logic operators with parentheses
        ("where (type=\"text\" and visible)", "Logic with parentheses"),
        ("where not disabled", "NOT operator"),

        # String operators
        ("where text contains \"Submit\"", "String contains"),
        ("where id starts \"user_\"", "String starts"),
        ("where name ends \"_input\"", "String ends"),
        ("where text matches \"[0-9]+\"", "String matches (regex)"),

        # Range syntax
        ("[1-10]", "Range selection"),
        ("[1,3,5-8,10]", "Mixed range selection"),

        # Boolean literals
        ("where visible = true", "Boolean true"),
        ("where disabled = false", "Boolean false"),

        # Complex conditions
        ("where (type=\"text\" or type=\"email\") and not disabled", "Complex condition"),
    ]

    for test_input, description in test_cases:
        print(f"\n[{description}]")
        print(f"  Input: {test_input}")

        try:
            tokens = lexer.tokenize(test_input)
            token_str = ", ".join([f"{t.type.name}" for t in tokens[:-1]])  # Skip EOF
            print(f"  Tokens: {token_str}")

            # Verify specific tokens
            if ">" in test_input and ">=" not in test_input:
                assert any(t.type == TokenType.GT for t in tokens), "Missing GT token"
            if ">=" in test_input:
                assert any(t.type == TokenType.GTE for t in tokens), "Missing GTE token"
            if "<" in test_input and "<=" not in test_input:
                assert any(t.type == TokenType.LT for t in tokens), "Missing LT token"
            if "<=" in test_input:
                assert any(t.type == TokenType.LTE for t in tokens), "Missing LTE token"
            if "(" in test_input:
                assert any(t.type == TokenType.LPAREN for t in tokens), "Missing LPAREN token"
            if ")" in test_input:
                assert any(t.type == TokenType.RPAREN for t in tokens), "Missing RPAREN token"
            if "contains" in test_input:
                assert any(t.type == TokenType.CONTAINS for t in tokens), "Missing CONTAINS token"
            if "starts" in test_input:
                assert any(t.type == TokenType.STARTS for t in tokens), "Missing STARTS token"
            if "ends" in test_input:
                assert any(t.type == TokenType.ENDS for t in tokens), "Missing ENDS token"
            if "matches" in test_input:
                assert any(t.type == TokenType.MATCHES for t in tokens), "Missing MATCHES token"
            if "-" in test_input and "\"" not in test_input:
                assert any(t.type == TokenType.DASH for t in tokens), "Missing DASH token"
            if "true" in test_input:
                assert any(t.type == TokenType.TRUE for t in tokens), "Missing TRUE token"
            if "false" in test_input:
                assert any(t.type == TokenType.FALSE for t in tokens), "Missing FALSE token"

            print("  [OK] All expected tokens present")

        except Exception as e:
            print(f"  [ERROR] {e}")
            return False

    print("\n" + "="*60)
    print("[OK] All Phase 2 lexer tests passed!")
    print("="*60)
    return True


if __name__ == '__main__':
    success = test_phase2_tokens()
    sys.exit(0 if success else 1)

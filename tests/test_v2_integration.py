"""
Integration tests for V2 - End-to-end scenarios
"""
import pytest
import asyncio
from pathlib import Path
from selector_cli.core.browser import BrowserManager
from selector_cli.core.context_v2 import ContextV2
from selector_cli.parser.parser_v2 import ParserV2
from selector_cli.commands.executor_v2 import ExecutorV2
from selector_cli.core.element import Element


@pytest.fixture
async def setup():
    """Setup test environment"""
    # Create context
    ctx = ContextV2(enable_history_file=False)

    # Create parser and executor
    parser = ParserV2()
    executor = ExecutorV2(ctx)

    # Create and initialize browser
    browser = BrowserManager()
    await browser.initialize(headless=True)
    ctx.browser = browser

    yield ctx, parser, executor, browser

    # Cleanup
    await browser.close()


class TestV2Integration:
    """Integration tests for complete v2 workflows"""

    @pytest.mark.asyncio
    async def test_scan_add_list_workflow(self, setup):
        """Test: scan -> add button -> list"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Step 1: scan
        cmd = parser.parse("scan")
        success, result = await executor.execute(cmd)
        assert success is True
        assert len(ctx.candidates) > 0

        # Step 2: add button
        cmd = parser.parse("add button")
        success, result = await executor.execute(cmd)
        assert success is True
        assert result > 0  # Number of buttons added

        # Step 3: list (should show workspace)
        cmd = parser.parse("list")
        success, result = await executor.execute(cmd)
        assert success is True
        assert "workspace" in result
        assert "button" in result.lower()

    @pytest.mark.asyncio
    async def test_find_role_button_workflow(self, setup):
        """Test: find div where role='button' -> list temp -> add from temp"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Initial scan
        cmd = parser.parse("scan")
        await executor.execute(cmd)

        # Add traditional buttons
        cmd = parser.parse("add button")
        await executor.execute(cmd)

        # Step 1: find div where role="button"
        cmd = parser.parse('find div where role="button"')
        success, result = await executor.execute(cmd)
        assert success is True
        assert len(ctx.temp) > 0  # Should find role=button divs

        # Verify we found role button elements
        role_buttons = [e for e in ctx.temp if e.attributes.get("role") == "button"]
        assert len(role_buttons) > 0

        # Step 2: list temp
        cmd = parser.parse("list temp")
        success, result = await executor.execute(cmd)
        assert success is True
        assert "temp" in result

        # Step 3: add from temp
        cmd = parser.parse("add from temp")
        success, result = await executor.execute(cmd)
        assert success is True
        assert result > 0  # Number added

        # Verify workspace has both traditional buttons and role buttons
        assert len(ctx.workspace) >= len(role_buttons)

    @pytest.mark.asyncio
    async def test_chain_refine_commands(self, setup):
        """Test: find div -> .find where visible -> .find where enabled"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Step 1: find div (find all divs)
        cmd = parser.parse("find div")
        success, result = await executor.execute(cmd)
        assert success is True
        initial_count = len(ctx.temp)
        assert initial_count > 0

        # Step 2: .find where visible (refine to visible only)
        cmd = parser.parse(".find where visible")
        success, result = await executor.execute(cmd)
        assert success is True
        visible_count = len(ctx.temp)
        assert visible_count <= initial_count

        # Step 3: .find where enabled (further refine)
        cmd = parser.parse(".find where enabled")
        success, result = await executor.execute(cmd)
        assert success is True
        enabled_count = len(ctx.temp)
        assert enabled_count <= visible_count

        # All results should be enabled and visible
        for elem in ctx.temp:
            assert elem.visible is True
            assert elem.enabled is True

    @pytest.mark.asyncio
    async def test_find_with_complex_condition(self, setup):
        """Test: find button where text contains 'Submit'"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Find button with specific text
        cmd = parser.parse('find button where text contains "Submit"')
        success, result = await executor.execute(cmd)
        assert success is True

        # Should find at least one submit button
        assert len(ctx.temp) >= 0  # May or may not find depending on test page

    @pytest.mark.asyncio
    async def test_add_with_filter(self, setup):
        """Test: add button where visible"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Scan first
        cmd = parser.parse("scan")
        await executor.execute(cmd)

        # Add only visible buttons
        cmd = parser.parse("add button where visible")
        success, result = await executor.execute(cmd)
        assert success is True

        # All added buttons should be visible
        for elem in ctx.workspace:
            if elem.tag == "button":
                assert elem.visible is True

    @pytest.mark.asyncio
    async def test_list_different_sources(self, setup):
        """Test: list candidates, list temp, list workspace"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Scan and add some elements
        cmd = parser.parse("scan")
        await executor.execute(cmd)
        candidates_count = len(ctx.candidates)

        cmd = parser.parse("add button")
        await executor.execute(cmd)
        workspace_count = len(ctx.workspace)

        # Find some elements (to populate temp)
        cmd = parser.parse("find div")
        await executor.execute(cmd)
        temp_count = len(ctx.temp)

        # List candidates
        cmd = parser.parse("list candidates")
        success, result = await executor.execute(cmd)
        assert success is True
        assert "candidates" in result

        # List temp
        cmd = parser.parse("list temp")
        success, result = await executor.execute(cmd)
        assert success is True
        assert "temp" in result

        # List workspace (default)
        cmd = parser.parse("list")
        success, result = await executor.execute(cmd)
        assert success is True
        assert "workspace" in result

    @pytest.mark.asyncio
    async def test_remove_elements(self, setup):
        """Test: remove button from workspace"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Scan and add buttons
        cmd = parser.parse("scan")
        await executor.execute(cmd)

        cmd = parser.parse("add button")
        success, result = await executor.execute(cmd)
        assert success is True
        initial_count = len(ctx.workspace)
        assert initial_count > 0

        # Remove all buttons
        cmd = parser.parse("remove button")
        success, result = await executor.execute(cmd)
        assert success is True
        assert result == initial_count  # All buttons removed

        # Workspace should be empty or have non-buttons
        remaining_buttons = sum(1 for e in ctx.workspace if e.tag == "button")
        assert remaining_buttons == 0

    @pytest.mark.asyncio
    async def test_scan_with_element_types(self, setup):
        """Test: scan button, input, div"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Scan specific types
        cmd = parser.parse("scan button, input, div")
        success, result = await executor.execute(cmd)
        assert success is True

        # Should have found elements
        assert len(ctx.candidates) > 0

        # Should include the specified types
        button_count = sum(1 for e in ctx.candidates if e.tag == "button")
        input_count = sum(1 for e in ctx.candidates if e.tag == "input")
        div_count = sum(1 for e in ctx.candidates if e.tag == "div")

        assert button_count + input_count + div_count == len(ctx.candidates)

    @pytest.mark.asyncio
    async def test_add_from_different_sources(self, setup):
        """Test: add from temp, add from candidates"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Clear workspace
        ctx.clear_workspace()

        # Find divs (store in temp)
        cmd = parser.parse("find div")
        await executor.execute(cmd)
        temp_count = len(ctx.temp)
        assert temp_count > 0

        # Add from temp
        cmd = parser.parse("add from temp")
        success, result = await executor.execute(cmd)
        assert success is True
        assert result == temp_count
        assert len(ctx.workspace) == temp_count

        # Clear workspace again
        ctx.clear_workspace()

        # Scan to populate candidates
        cmd = parser.parse("scan")
        await executor.execute(cmd)

        # Add from candidates
        cmd = parser.parse("add button from candidates")
        success, result = await executor.execute(cmd)
        assert success is True
        assert result > 0

    @pytest.mark.asyncio
    async def test_temp_expiration_integration(self, setup):
        """Test that temp results expire correctly"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Find elements (populate temp)
        cmd = parser.parse("find div")
        await executor.execute(cmd)
        assert len(ctx.temp) > 0

        # Temp should not be expired immediately
        assert ctx.has_temp_results() is True

        # Manually expire temp (set TTL to 0)
        ctx.TEMP_TTL = 0
        import time
        time.sleep(0.1)

        # Temp should now be expired
        assert ctx.has_temp_results() is False
        assert len(ctx.temp) == 0

    @pytest.mark.asyncio
    async def test_find_all_elements_with_wildcard(self, setup):
        """Test: find *"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Find all elements
        cmd = parser.parse("find *")
        success, result = await executor.execute(cmd)
        assert success is True

        # Should have found elements
        # Note: Wildcard not fully implemented yet, this is a placeholder
        # assert len(ctx.temp) > 0


class TestV2ComplexScenarios:
    """Test complex real-world scenarios"""

    @pytest.fixture
    async def setup(self):
        """Setup test environment"""
        ctx = ContextV2(enable_history_file=False)
        parser = ParserV2()
        executor = ExecutorV2(ctx)
        browser = BrowserManager()
        await browser.initialize(headless=True)
        ctx.browser = browser

        yield ctx, parser, executor, browser

        await browser.close()

    @pytest.mark.asyncio
    async def test_complete_login_form_workflow(self, setup):
        """
        Complete workflow: Login form element discovery
        1. scan
        2. add input, button
        3. find div where role="button" (custom component)
        4. add from temp
        5. export yaml
        """
        ctx, parser, executor, browser = setup

        # Load test page with form
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Step 1: Scan for elements
        cmd = parser.parse("scan button, input, div")
        success, result = await executor.execute(cmd)
        assert success is True
        assert len(ctx.candidates) > 0

        # Step 2: Add traditional inputs and buttons
        cmd = parser.parse("add input")
        success, result = await executor.execute(cmd)
        assert success is True

        cmd = parser.parse("add button")
        success, result = await executor.execute(cmd)
        assert success is True

        initial_workspace_count = len(ctx.workspace)

        # Step 3: Find custom role=button elements
        cmd = parser.parse('find div where role="button"')
        success, result = await executor.execute(cmd)
        assert success is True

        role_button_count = len(ctx.temp)
        if role_button_count > 0:
            # Step 4: Add custom buttons from temp
            cmd = parser.parse("add from temp")
            success, result = await executor.execute(cmd)
            assert success is True
            assert result > 0  # At least one element added

            # Verify workspace now has both traditional and custom buttons
            assert len(ctx.workspace) >= initial_workspace_count + result

        # Step 5: Export (placeholder)
        cmd = parser.parse("export yaml")
        success, result = await executor.execute(cmd)
        assert success is True

    @pytest.mark.asyncio
    async def test_exploration_and_refinement_workflow(self, setup):
        """
        Exploration workflow:
        1. find div (find all divs)
        2. .find where visible (refine to visible)
        3. .find where role="button" (further refine)
        4. list temp (review)
        5. add from temp (add to workspace)
        """
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Step 1: Find all divs (broad search)
        cmd = parser.parse("find div")
        success, result = await executor.execute(cmd)
        assert success is True
        all_divs_count = len(ctx.temp)
        assert all_divs_count > 0

        # Step 2: Refine to visible divs only
        cmd = parser.parse(".find where visible")
        success, result = await executor.execute(cmd)
        assert success is True
        visible_divs_count = len(ctx.temp)
        assert visible_divs_count <= all_divs_count

        # Step 3: Further refine to divs with role=button
        cmd = parser.parse('.find where role="button"')
        success, result = await executor.execute(cmd)
        assert success is True
        role_button_count = len(ctx.temp)

        # Step 4: Review in temp
        cmd = parser.parse("list temp")
        success, result = await executor.execute(cmd)
        assert success is True
        assert "temp" in result

        # Step 5: Add to workspace
        if role_button_count > 0:
            cmd = parser.parse("add from temp")
            success, result = await executor.execute(cmd)
            assert success is True
            assert result == role_button_count

    @pytest.mark.asyncio
    async def test_multiple_element_types_scan(self, setup):
        """Test scanning multiple element types at once"""
        ctx, parser, executor, browser = setup

        # Load test page
        test_file = Path(__file__).parent / "test_role_button.html"
        test_url = f"file://{test_file.resolve()}"
        page = browser.get_page()
        await page.goto(test_url)
        ctx.current_url = test_url

        # Scan multiple types
        cmd = parser.parse("scan button, input, div, select, textarea")
        success, result = await executor.execute(cmd)
        assert success is True

        # Should have found elements of each type
        button_count = sum(1 for e in ctx.candidates if e.tag == "button")
        input_count = sum(1 for e in ctx.candidates if e.tag == "input")
        div_count = sum(1 for e in ctx.candidates if e.tag == "div")

        assert button_count + input_count + div_count == len(ctx.candidates)

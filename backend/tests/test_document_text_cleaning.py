from app.services.document_text_cleaning import (
    DocumentTextCleaningService,
)


def test_clean_empty_text():
    """Verify that empty text returns an empty string."""

    service = DocumentTextCleaningService()

    result = service.clean("")

    assert result == ""


def test_clean_normalizes_line_endings():
    """Verify that line endings are normalized."""

    service = DocumentTextCleaningService()

    text = "Employee Handbook\r\nCompany Policies\rAnother Line"

    result = service.clean(text)

    assert result == (
        "Employee Handbook\n"
        "Company Policies\n"
        "Another Line"
    )


def test_clean_normalizes_spaces_and_tabs():
    """Verify that unnecessary spaces and tabs are normalized."""

    service = DocumentTextCleaningService()

    text = "Employee     Handbook\nCompany\t\tHR\tPolicies"

    result = service.clean(text)

    assert result == (
        "Employee Handbook\n"
        "Company HR Policies"
    )


def test_clean_removes_null_characters():
    """Verify that null characters are removed."""

    service = DocumentTextCleaningService()

    text = "Employee\x00 Handbook\x00"

    result = service.clean(text)

    assert result == "Employee Handbook"


def test_clean_limits_blank_lines():
    """Verify that excessive blank lines are reduced."""

    service = DocumentTextCleaningService()

    text = (
        "Employee Handbook\n"
        "\n"
        "\n"
        "\n"
        "Company Policies"
    )

    result = service.clean(text)

    assert result == (
        "Employee Handbook\n\n"
        "Company Policies"
    )


def test_clean_strips_outer_whitespace():
    """Verify that whitespace around the document is removed."""

    service = DocumentTextCleaningService()

    text = "\n\n  Employee Handbook  \n\n"

    result = service.clean(text)

    assert result == "Employee Handbook"


def test_clean_preserves_paragraph_separation():
    """Verify that meaningful paragraph separation is preserved."""

    service = DocumentTextCleaningService()

    text = (
        "Employee Handbook\n\n"
        "Company Policies\n\n"
        "Leave Policy"
    )

    result = service.clean(text)

    assert result == (
        "Employee Handbook\n\n"
        "Company Policies\n\n"
        "Leave Policy"
    )

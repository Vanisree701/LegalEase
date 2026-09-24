import html
import os
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv

from utils.document_formatter import (
    format_docx,
    format_pdf
)

from utils.text_utils import (
    safe_filename,
    sanitize_text
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


# --------------------------------------------------
# Streamlit configuration
# --------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .preview {
        background: #111827;
        color: #f9fafb;
        padding: 22px;
        border-radius: 12px;
        min-height: 400px;
        max-height: 650px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.6;
    }

    .notice {
        padding: 12px 16px;
        border-left: 4px solid #6b7280;
        background: #f3f4f6;
        border-radius: 4px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="notice">'
    '<b>Notice:</b> LegalEase creates drafts for '
    'educational and drafting purposes. Review the '
    'final document with a qualified legal professional '
    'before signing or relying on it.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header(
        "Document Details"
    )

    document_type = st.text_input(
        "Document Type",
        value="Freelance Work Contract",
        help=(
            "Examples: NDA, Lease Agreement, "
            "Employment Contract"
        )
    )

    parties = st.text_area(
        "Parties Involved",
        value=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=110
    )

    terms = st.text_area(
        "Terms & Conditions",
        value=(
            "Payment to be made within 30 days of invoice; "
            "The provider agrees to deliver work by the "
            "agreed deadline; "
            "Confidentiality must be maintained at all times; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
        help=(
            "Separate individual terms using semicolons."
        )
    )

    effective_date = st.text_input(
        "Effective Date",
        value=date.today().strftime(
            "%B %d, %Y"
        )
    )

    generate_button = st.button(
        "Generate Document",
        type="primary",
        use_container_width=True
    )


# --------------------------------------------------
# Generate document
# --------------------------------------------------

if generate_button:

    if not document_type.strip():

        st.error(
            "Please enter the document type."
        )

    elif not parties.strip():

        st.error(
            "Please enter the parties."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms."
        )

    elif not effective_date.strip():

        st.error(
            "Please enter the effective date."
        )

    else:

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",

                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "effective_date": effective_date
                    },

                    timeout=120
                )

                if response.ok:

                    data = response.json()

                    st.session_state.document = (
                        sanitize_text(
                            data["document"]
                        )
                    )

                    st.success(
                        "Document generated successfully."
                    )

                else:

                    try:

                        error_message = (
                            response.json()
                            .get(
                                "detail",
                                response.text
                            )
                        )

                    except Exception:

                        error_message = (
                            response.text
                        )

                    st.error(
                        f"Backend error: {error_message}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Could not connect to the FastAPI "
                    "backend."
                )

                st.info(
                    "Make sure the backend is running "
                    "on port 8000."
                )

                st.caption(
                    str(exc)
                )


# --------------------------------------------------
# Preview
# --------------------------------------------------

st.subheader(
    "Document Preview"
)


if st.session_state.document:

    safe_html = html.escape(
        st.session_state.document
    )

    st.markdown(
        f'<div class="preview">{safe_html}</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # Editable document
    # --------------------------------------------------

    st.subheader(
        "Edit Document"
    )

    edited_document = st.text_area(
        "Modify the generated document below:",
        value=st.session_state.document,
        height=500,
        label_visibility="collapsed"
    )

    st.session_state.document = (
        edited_document
    )

    # --------------------------------------------------
    # Filename
    # --------------------------------------------------

    base_name = safe_filename(
        document_type
    )

    # --------------------------------------------------
    # Download buttons
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    # TXT
    with col1:

        st.download_button(
            label="Download TXT",

            data=(
                st.session_state.document
                .encode("utf-8")
            ),

            file_name=f"{base_name}.txt",

            mime="text/plain",

            use_container_width=True
        )

    # DOCX
    with col2:

        docx_data = format_docx(
            st.session_state.document,
            document_type
        )

        st.download_button(
            label="Download DOCX",

            data=docx_data,

            file_name=f"{base_name}.docx",

            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),

            use_container_width=True
        )

    # PDF
    with col3:

        pdf_data = format_pdf(
            st.session_state.document,
            document_type
        )

        st.download_button(
            label="Download PDF",

            data=pdf_data,

            file_name=f"{base_name}.pdf",

            mime="application/pdf",

            use_container_width=True
        )

else:

    st.info(
        "Enter the document details in the sidebar "
        "and click Generate Document."
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "LegalEase • FastAPI + Streamlit + Gemini • "
    "AI-assisted legal drafting"
)
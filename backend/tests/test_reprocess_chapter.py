import asyncio

from nlp_engine.document.processor import process_pdf


PDF_PATH = r"C:\Users\shrut\Downloads\ncert-test\gecu101.pdf"


async def main():

    print("\nREPROCESSING NCERT PDF")
    print("=" * 60)

    result = process_pdf(PDF_PATH)

    print("Pages:", result["page_count"])
    print("Cleaned text length:", result["text_length"])

    print("\nDETECTED CHAPTERS")
    print("=" * 60)

    for chapter in result["chapters"]:
        print(
            f"Chapter {chapter['chapter_number']}: "
            f"{chapter['title']} "
            f"(pages {chapter['start_page']}-"
            f"{chapter['end_page']})"
        )

    print("\nCLEANED TEXT PREVIEW")
    print("=" * 60)

    print(result["cleaned_text"][:5000])


if __name__ == "__main__":
    asyncio.run(main())
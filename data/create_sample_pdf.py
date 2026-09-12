import os


def generate_sample_transcript(pdf_path: str = "data/sample_transcript.pdf"):
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    lines = [
        "METROPOLITAN STATE UNIVERSITY",
        "OFFICIAL ACADEMIC TRANSCRIPT",
        "Student Name: Jane Doe    Student ID: STU-882104",
        "Degree Program: B.S. Computer Science    Minor: Artificial Intelligence",
        "Cumulative GPA: 3.82    Status: Active / Good Standing",
        "",
        "Completed Coursework:",
        "CS101 Introduction to Computer Science 4 A Fall 2023",
        "MATH201 Calculus I 4 A- Fall 2023",
        "ENG101 College Writing and Composition 3 A Fall 2023",
        "CS102 Data Structures and Algorithms 4 A Spring 2024",
        "MATH202 Linear Algebra and Differential Eq 4 B+ Spring 2024",
        "PHYS101 General Physics with Laboratory 4 B Spring 2024",
        "CS201 Computer Systems and Architecture 3 A Fall 2024",
        "MATH301 Probability and Statistics for CS 3 A- Fall 2024"
    ]

    stream_content = "BT\n/F1 12 Tf\n50 720 Td\n18 TL\n"
    for line in lines:
        escaped = line.replace("(", "\\(").replace(")", "\\)")
        stream_content += f"({escaped}) '\n"
    stream_content += "ET\n"

    stream_bytes = stream_content.encode("latin1")
    stream_len = len(stream_bytes)

    pdf_template = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(stream_len).encode("ascii") + b" >>\nstream\n" +
        stream_bytes +
        b"\nendstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000222 00000 n \n"
        b"0000000000 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n500\n%%EOF\n"
    )

    with open(pdf_path, "wb") as f:
        f.write(pdf_template)

    print(f"Sample transcript generated: {pdf_path}")


if __name__ == "__main__":
    generate_sample_transcript()

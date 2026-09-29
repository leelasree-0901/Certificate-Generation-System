import csv
import os
import uuid
import zipfile
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

import database as db
from config import Config


def read_data(file_path):
    extension = file_path.rsplit(".", 1)[1].lower()

    if extension == "csv":
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return list(csv.DictReader(file))

    if extension == "xlsx":
        try:
            import openpyxl
        except ImportError:
            raise Exception(
                "openpyxl is required for XLSX files."
            )

        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook.active

        rows = list(sheet.values)

        if not rows:
            return []

        headers = [
            str(value).strip() if value is not None else ""
            for value in rows[0]
        ]

        return [
            dict(zip(headers, row))
            for row in rows[1:]
        ]

    raise Exception("Only CSV and XLSX files are supported.")


def get_value(row, possible_names, default=""):
    for name in possible_names:
        if name in row and row[name] not in (None, ""):
            return str(row[name]).strip()

    lower_map = {
        str(key).lower().strip(): value
        for key, value in row.items()
    }

    for name in possible_names:
        value = lower_map.get(name.lower())

        if value not in (None, ""):
            return str(value).strip()

    return default


def get_font(size, bold=False):
    candidates = []

    if bold:
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf"
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf"
        ]

    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def create_certificate(
    participant_name,
    course,
    issue_date,
    certificate_id,
    template_path=None
):
    width = 1600
    height = 1100

    if template_path and os.path.exists(template_path):
        image = Image.open(template_path).convert("RGB")
        image = image.resize((width, height))
    else:
        image = Image.new(
            "RGB",
            (width, height),
            "white"
        )

    draw = ImageDraw.Draw(image)

    title_font = get_font(70, True)
    name_font = get_font(65, True)
    normal_font = get_font(35)
    small_font = get_font(25)

    title = "CERTIFICATE"

    title_box = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_box[2] - title_box[0]

    draw.text(
        ((width - title_width) / 2, 120),
        title,
        fill="black",
        font=title_font
    )

    subtitle = "This certificate is proudly presented to"

    subtitle_box = draw.textbbox(
        (0, 0),
        subtitle,
        font=normal_font
    )

    subtitle_width = subtitle_box[2] - subtitle_box[0]

    draw.text(
        ((width - subtitle_width) / 2, 280),
        subtitle,
        fill="black",
        font=normal_font
    )

    name_box = draw.textbbox(
        (0, 0),
        participant_name,
        font=name_font
    )

    name_width = name_box[2] - name_box[0]

    draw.text(
        ((width - name_width) / 2, 390),
        participant_name,
        fill="black",
        font=name_font
    )

    course_text = f"For successful completion of {course}"

    course_box = draw.textbbox(
        (0, 0),
        course_text,
        font=normal_font
    )

    course_width = course_box[2] - course_box[0]

    draw.text(
        ((width - course_width) / 2, 520),
        course_text,
        fill="black",
        font=normal_font
    )

    date_text = f"Issue Date: {issue_date}"

    draw.text(
        (180, 850),
        date_text,
        fill="black",
        font=small_font
    )

    draw.text(
        (1100, 850),
        f"Certificate ID: {certificate_id}",
        fill="black",
        font=small_font
    )

    filename = f"{certificate_id}.png"

    output_path = os.path.join(
        Config.CERT_FOLDER,
        filename
    )

    image.save(output_path)

    return output_path


def generate_all(data_path, template_path=None, settings=None):
    os.makedirs(Config.CERT_FOLDER, exist_ok=True)
    os.makedirs(Config.ZIP_FOLDER, exist_ok=True)

    settings = settings or {}

    rows = read_data(data_path)

    generated = []
    errors = []

    if not rows:
        return {
            "ok": False,
            "generated": [],
            "errors": ["No participant data found."],
            "zip": None
        }

    for index, row in enumerate(rows, start=1):
        try:
            participant_name = get_value(
                row,
                ["participant_name", "name", "Name", "Participant Name"],
                f"Participant {index}"
            )

            course = get_value(
                row,
                ["course", "Course"],
                settings.get(
                    "course",
                    "Certificate of Participation"
                )
            )

            email = get_value(
                row,
                ["email", "Email", "email_address"],
                ""
            )

            issue_date = get_value(
                row,
                ["issue_date", "date", "Date"],
                datetime.now().strftime("%d-%m-%Y")
            )

            certificate_id = (
                f"CERT-{datetime.now().strftime('%Y%m%d')}-"
                f"{uuid.uuid4().hex[:6].upper()}"
            )

            file_path = create_certificate(
                participant_name,
                course,
                issue_date,
                certificate_id,
                template_path
            )

            db.add_certificate(
                certificate_id,
                participant_name,
                course,
                email,
                issue_date,
                file_path
            )

            generated.append({
                "certificate_id": certificate_id,
                "participant_name": participant_name,
                "file": os.path.basename(file_path)
            })

        except Exception as error:
            errors.append(
                f"Row {index}: {str(error)}"
            )

    zip_name = f"certificates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    zip_path = os.path.join(
        Config.ZIP_FOLDER,
        zip_name
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        for item in generated:
            file_path = os.path.join(
                Config.CERT_FOLDER,
                item["file"]
            )

            if os.path.exists(file_path):
                zip_file.write(
                    file_path,
                    arcname=item["file"]
                )

    return {
        "ok": len(generated) > 0,
        "generated": generated,
        "errors": errors,
        "zip": zip_name
    }
from pathlib import Path

from PIL import Image


def run_ocr_no_cluster(img_path: Path):
    import pytesseract
    from pytesseract import Output

    custom_config = (
        ""
        # "digits"
        # r"--oem 3 "
        # r"--psm 11 "
        # r"--dpi 2000"
        # r"-c tessedit_char_whitelist='0123456789'"
    )

    boxes = pytesseract.image_to_boxes(
        Image.open(str(img_path)),
        output_type=Output.DICT,
        config=custom_config,
    )

    return boxes


def run_ocr_no_boxes(img_path: Path):
    import pytesseract

    custom_config = (
        "digits"
        # r"--oem 3 "
        # r"--psm 11 "
        # r"--dpi 2000"
        # r"-c tessedit_char_whitelist='0123456789'"
    )

    return pytesseract.image_to_string(
        Image.open(str(img_path)),
        config=custom_config,
    )


def run_ocr_confidence(img_path):
    custom_config = (
        "digits"
        # r"--oem 3 "
        # r"--psm 11 "
        # r"--dpi 2000"
        # r"-c tessedit_char_whitelist='0123456789'"
    )

    import pytesseract
    from pytesseract import Output

    import cv2

    img = cv2.imread(str(img_path))

    detection = pytesseract.image_to_data(
        img,
        output_type=Output.DICT,
        config=custom_config,
    )

    n_boxes = len(detection["level"])
    for i in range(n_boxes):
        confidence = 0.6

        if detection["conf"][i] < confidence:
            continue

        (x, y, w, h) = (
            detection["left"][i],
            detection["top"][i],
            detection["width"][i],
            detection["height"][i],
        )
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
        cv2.putText(
            img,
            f'({detection["text"][i]})',
            (x + 4, y + 14),
            cv2.FONT_HERSHEY_COMPLEX,
            0.3,
            color=(0, 255, 0),
        )

    cv2.imshow("img", img)
    cv2.waitKey(0)


def run_ocr2(img_path):
    import tesserocr
    from PIL import Image

    api = tesserocr.PyTessBaseAPI()
    api.SetImage(Image.open(str(img_path)))
    text = api.GetUTF8Text()
    print(text)


if __name__ == "__main__":
    run_ocr_no_cluster(
        Path.home() / "Downloads" / "Cross_Creek_Siteplan_TOURGUIDE_230421.png"
    )

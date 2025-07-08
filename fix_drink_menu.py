import csv

INPUT_CSV  = 'drink_menu.txt'
OUTPUT_CSV = 'drink_menu.csv'

with open(INPUT_CSV, newline='', encoding='utf-8') as infile, \
     open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

    # 헤더 그대로 복사
    header = next(reader)
    writer.writerow(header)

    for row in reader:
        # 쉼표로 인해 분리된 여러 칸을 합쳐서 '추천 안주' 필드로 복원
        drink, *rest = row
        snack = ','.join(rest).strip()
        writer.writerow([drink, snack])

print(f'완료: {OUTPUT_CSV} 생성됨')
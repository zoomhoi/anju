import csv

INPUT_CSV  = 'food_menu.csv'
OUTPUT_CSV = 'food_menu_fixed.csv'

with open(INPUT_CSV, newline='', encoding='utf-8') as infile, \
     open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

    # 헤더 그대로 복사
    header = next(reader)
    writer.writerow(header)

    for row in reader:
        # 쉼표로 인해 분리된 여러 칸을 합쳐서 '음식명' 필드로 복원
        cat, sub, *rest = row
        name = ','.join(rest).strip()
        writer.writerow([cat, sub, name])

print(f'완료: {OUTPUT_CSV} 생성됨')

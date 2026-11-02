# diet-chy 데이터 연결 파일

이 폴더의 CSV 3개는 서로 역할이 다릅니다.

## 파일 설명
- `food_catalog.csv`: 검색할 음식 목록입니다. 일반 음식과 가공식품이 한 파일에 들어 있습니다.
- `nutrition_data.csv`: 영양성분 원자료를 앱에서 쓰기 쉽게 정리한 표입니다. `food_code`가 고유 식별자입니다.
- `food_nutrition_links.csv`: 음식 목록과 영양성분을 연결하는 표입니다. `catalog_id`와 `food_code`를 이용합니다.

## 연결 방식
1. 앱에서 `food_catalog.csv`의 `food_name`을 검색합니다.
2. 선택한 음식의 `catalog_id`를 얻습니다.
3. `food_nutrition_links.csv`에서 같은 `catalog_id`의 `food_code`를 찾습니다.
4. `nutrition_data.csv`에서 같은 `food_code`의 영양성분을 가져옵니다.

## 꼭 알아둘 점
- 이름을 공백·유니코드 표기 차이만 정리한 뒤 **정확히 일치하는 경우만** 연결했습니다. 비슷해 보이는 이름을 임의로 연결하지 않았습니다.
- `match_status`가 `미연결`이면 영양성분을 찾지 못한 음식입니다. 이 경우 영양값을 임의로 표시하면 안 됩니다.
- `동일 이름 후보 여러 개`는 같은 음식명에 영양성분 자료가 여러 건 있다는 뜻입니다. 조리법·데이터구분·기준량을 확인한 뒤 하나를 선택해야 합니다.
- 영양성분은 `nutrient_basis` 기준입니다. `100g`과 `100ml`를 구분하세요. 특히 ml 기준 자료를 g 기준으로 그대로 계산하면 안 됩니다.
- 현재 파일은 우선 연결 구조를 만든 1차 결과입니다. 정확한 음식별 영양값 선택 규칙은 다음 단계에서 앱에 적용합니다.

## 기본 사용 예시 (main.py에서)
```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

catalog = pd.read_csv(DATA_DIR / "food_catalog.csv", encoding="utf-8-sig")
links = pd.read_csv(DATA_DIR / "food_nutrition_links.csv", encoding="utf-8-sig")
nutrition = pd.read_csv(DATA_DIR / "nutrition_data.csv", encoding="utf-8-sig")

# 선택한 catalog_id로 연결된 영양성분 코드 찾기
selected_id = "F000001"
codes = links.loc[links["catalog_id"] == selected_id, "food_code"]

# 연결된 영양성분 행 가져오기
result = nutrition[nutrition["food_code"].isin(codes)]
```

## 연결 결과 요약
- 일반 음식 검색 항목: 15,658개
- 가공식품 검색 항목: 43,028개
- 영양성분 원자료: 50,000개
- 이름 기준 연결 관계: 55,682개
- 연결된 검색 항목: 41,812개 / 58,686개

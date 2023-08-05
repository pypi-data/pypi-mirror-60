# Use

- pip install

```bash
#pip install shholiday
```


- Temporary use

```python
from shholiday import holiday2020

daytuple = (1,1) # 1월 1일이 휴일인지 확인하고 싶을 때
nowholiday = holiday2020()
print(nowholiday.is_holiday(daytuple))
```

- Check if today's date is a holiday

```python
from shholiday import holiday2020
from datetime import  datetime

    
now = datetime.now()
daytuple = (str(now.month),str(now.day))

nowholiday = holiday2020()
print(nowholiday.is_holiday(daytuple))
```
# Введение
pybeandi - Это библиотека, реализующая внедрение зависимостей в Python

## Описание
Главным объектом во всей библиотеке является **бин** (bean).
Бины определяются, создаются и управляются **контекстом** (BeanContext).
Вы можете внедрять их в другие бины или запрашивать их от самого контекста.
Тем самым ваш код больше не знает, какие именно объекты к нему приходят, 
что уменьшает связанность объектов и упрощает поддержку и читаемость, 
так как теперь управлением вашими объектами и их зависимостями управляет контекст.

## Пример

```python
import abc

from pybeandi.context import BeanContextBuilder
from pybeandi.decorators import bean


class Service(abc.ABC):

    @abc.abstractmethod
    def hello(self) -> str:
        pass


@bean(profiles={'service1'})
class My1Service(Service):

    def hello(self) -> str:
        return 'Hello from 1 service'


@bean(profiles={'service2'})
class My2Service(Service):

    def hello(self) -> str:
        return 'Hello from 2 service'


@bean(profiles={'service3'}, context='context')
class My3Service(Service):

    def hello(self) -> str:
        return f'Hello from 3 service and {self.context.beans[Service]}'

    def __init__(self, context):
        self.context = context


@bean()
def failed_bean():
    pass


if __name__ == '__main__':
    ctx_builder = BeanContextBuilder()
    ctx_builder.load_yaml('pybeandi.yaml')
    ctx_builder.profiles.add('service3')
    ctx_builder.scan(globals())
    ctx = ctx_builder.init()

    print(ctx.beans[Service].hello())
    print(Service in ctx.beans)
    print(ctx.beans)
    print(ctx.profiles)
    print(set(ctx.beans.values()))

```

# Теория
Каждый бин обладает:
 - уникальным идендификаторов (**bean_id**), который однозначно определяет его внутри контекста;
 - конструктором (**factory_func**), который создаёт объект бина
 - словарём зависимостей (**dependencies**), который указывает, какому полю конструктора соответствует какой бин
 - функцией профиля (**profile_func**), которая принимает на вход список всех активных профилей и возвращает, нужно ли создавать бин

# Краткое описание инициализации контекста
Для создания контекста необходимо создать и настроить `BeanContextBuilder`,
 затем вызвать его метод `init()`, результатом которого будет сам `BeanContext`
 
 ```python
ctx_builder = BeanContextBuilder()
ctx_builder.load_yaml('pybeandi.yaml')
ctx_builder.profiles.add('service3')
ctx_builder.scan(globals())
ctx = ctx_builder.init()
...
```

## Способы определения объектов
Существует несколько способов сообщить контексту, что данный объект является бинов и отдать его под его контроль.

### Напрямую через метод
Этот метод в основном используется внутри библиотеки.

Синтаксис:
```python
ctx_builder.register_bean(bean_id: str,
                  factory_func: Callable[..., Any],
                  dependencies: Dict[str, str],
                  profile_func: Callable[[Set[str]], bool] = lambda profs: True)

# Если класс декорирован @bean
ctx_builder.register_bean_by_class(Service)
```

### Добавление вручную
Полезно для добавления строк, списков или других уже готовых объектов как бинов.

Синтаксис:
```python
ctx_builder.add_as_bean(bean_id: str, obj: Any)
```

### Сканирование

#### Через декорирование класса
Позволяет задеклорировать бин, не создавая лишних сущностей.

Синтаксис:
```python
@bean(bean_id: str,
      profiles: Set[str] = None,
      profile_func: Callable[[Set[str]], bool] = lambda profs: True,
      **depends_on: Dict[str, str])
class MyService(Service):

    def __init__(self, dep1, dep2, ...):
        ...

    ...
```

#### Через метод-фабрику
Этот метод полезен тогда, когда нет доступа к самому классу или для создания иного метода создания бина, 
чем у его конструктора.

Синтаксис:
```python
@bean(bean_id: str,
      profiles: Set[str] = None,
      profile_func: Callable[[Set[str]], bool] = lambda profs: True,
      **depends_on: Dict[str, str])
def factory_bean(dep1, dep2, ...):
    ...
    return obj
```

#### Автопоределения id
pybeandi поддерживают функцию автоопределения id бина, 
то есть необязательно явно указывать его id в декораторе. 
В этом случае он будет создан на основе название класса/функции.

```python
@bean() # id = my_service1
class MyService1:
    pass

@bean() #id = my_service2
def my_service2():
    pass
```

#### Важно
Если в коде используется декоратор `@bean`, то после необходимо обязательно вызвать 
```python
ctx_builder.scan(globals())
```
А декорированные классы и методы-фабрики должны находиться в области видимости

## Профили
Профили - это механизм управления инициализации сразу группой бинов в зависимости от настроек.
Так, например, если у вас есть две реализации одного интерфейса (абстрактного класса),
которые используются или в среде разработки, или в среде на "боевой" машине, то эти реализации могут иметь разные профили,
которые определяют что нужно загружать: реализацию для разработчиков или для клиентов.

### Задание профилей контекста
```python
ctx_builder.profiles.add('profile1')
```

### Задание профилей бина декоратором
Если необходимо только добавить условие, что все перечисленные профили должны быть активны, то достаточно
```python
@bean(..., profiles={'profile1', ...}, ...)
```

Если же условие сложнее, то необходимо задать функцию.
Так, например, если условием является то, что профиль 'profile1' нету в активных, то
```python
@bean(..., profile_func=lambda profs: 'profile1' not in profs, ...)
```

# Получение бинов
Для получения бинов из контекста можно воспользоваться несколькими способами

## Через зависимости
В параметр **dependencies** декоратора или функции необходимо задать словарь, 
где ключ - имя параметра в методе-фабрике или конструкторе, а значение - id нужного бина

```python
@bean(..., dep1='bean1', dep2='bean2')
class Bean3:
    def __init__(self, dep1, dep2):
        ...
```

```python
@bean(..., dep1='bean1', dep2='bean2')
def factory_bean3(dep1, dep2):
    ...
```

```python
ctx.register_bean(..., dependencies={
    'dep1': 'bean1',
    'dep2': 'bean2',
}, ...)
```

## Напрямую
Можно получить бин из самого объекта контекста по id или классу бина:

```python
bean3 = ctx.beans['bean3']
bean3 = ctx.beans[Bean3]
```
Причём, если запросить бин по классу, то будут искать все бины, которые являются объектом этого класса или его потомков.

## Дополнительно
```python
ctx.beans # доступ к бинам
ctx.beans.ids() # множество id бинов
ctx.beans.values() # список бинов без id
```

Узнать, существует ли бин с такой ссылкой, можно через
```python
Bean3 in ctx.beans
```
Причём если существует несколько подходящих бинов, то будет возвращено `True`

Контекст сам является бином, и его можно получить через внедрение зависимостей
```python
@bean(ctx=BeanContext)
class MyService:
    def __init__(self, ctx):
        pass
```

## Файл конфигурации
pybeandi позволяет задавать часть конфигурации через специальный YAML-файл. Его формат:

Также возможно использование переменных среды в конфигурации, тогда перед значением необходимо написать !ENV,
а переменные среды указывать как ${<Перемен. среды>}
```yaml
pybeandi:
    profiles:
      active:
        - profile1
        - ...
    beans:
      bean_id1: bean1
      service_vals:
        - val1
        - val2
      service_dict:
        key1: val1
        key2: val2
      db_url: !ENV jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_PATH}
```
`profiles.active` - активные профили

`beans` - бины базовых типов (строки, списки, словари и т.д.)

# Состояние разработки
pybeandi находится на стадии ранней разработки, что значит, что имена, сигнатуры и пути классов, методов и др. могут меняться без объявления. 

Если у Вас есть какие-либо пожелания/замечания по поводу библиотеки или хотите просто пообщаться:
[Telegram](https://tgmsg.ru/Discrimy) или в [Github Issues](https://github.com/Discrimy/pybeandi/issues)
# simplesrs

Simple SRS (spaced-recognition system) mechanism and database. Scalable and zero configuration.

## Usage

```python
>>> import simplesrs as srs
>>> srs.init('srs.db')
>>> srs.Card.add('类', tags=['hanzi', 't_hanzi1'], vocabs=['人类 人類 [ren2 lei4] humanity/human race/mankind'])
>>> srs.Card.add('数学', tags=['vocab', 'pleco'])
>>> srs.Card.add('重要的事情要立即去做', tags=['sentence', 't_hanzi1'], translation='重要的事情要立即去做。 [Zhòngyào de shìqing yào lìjí qù zuò. (Also no qu (less strong))] I need to go do important things immediately.')
>>> quiz = srs.Card.iter_quiz()
>>> card = next(quiz)
>>> card
重要的事情要立即去做
>>> card.info
{
    'translation':
        '重要的事情要立即去做。 [Zhòngyào de shìqing yào lìjí qù zuò. (Also no qu (less '
        'strong))] I need to go do important things immediately.'
}
```

## Installation

```
pip install simplesrs
```

## Related projects

- [ankix](https://github.com/patarapolw/ankix) -- New file format for Anki with improved review intervals. Pure peewee SQLite database, no zipfile, but media enabled. Available to work with on Jupyter Notebook. Full dropin replacement for Anki. 

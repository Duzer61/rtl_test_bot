import json
from datetime import datetime, timedelta

from aiogram.types import Message
from dateutil.relativedelta import relativedelta

from database.mongo_db import collection


def get_request_data(input_data: dict) -> tuple:
    """
    Извлекает из входящего сообщения данные запроса.
    """
    try:
        dt_from = input_data.get('dt_from')
        dt_upto = input_data.get('dt_upto')
        group_type = input_data.get('group_type')
        start_time: datetime = datetime.strptime(dt_from, '%Y-%m-%dT%H:%M:%S')
        end_time: datetime = datetime.strptime(dt_upto, '%Y-%m-%dT%H:%M:%S')
        if group_type not in ['hour', 'day', 'week', 'month']:
            raise Exception('Недопустимый интервал группировки.')
    except Exception:
        return Exception
    return group_type, start_time, end_time


def get_delta(group_type) -> timedelta:
    """
    Возвращает интервал времени для группировки.
    """
    intervals = {
        'hour': timedelta(hours=1),
        'day': timedelta(days=1),
        'week': timedelta(weeks=1),
        'month': relativedelta(months=1)
    }
    delta = intervals.get(group_type)
    return delta


def get_labels(start_time, end_time, group_type):
    """
    Генерация списка временных меток.
    """
    delta = get_delta(group_type)
    labels = []
    current_time = start_time
    while current_time <= end_time:
        labels.append(current_time)
        current_time += delta
    return labels


def get_pipeline(labels, i):
    """
    Возвращает пайплайн.
    """
    pipeline = [
        {
            '$match': {
                'dt': {
                    '$gte': labels[i],
                    (
                        '$lt' if i < len(labels) - 2 else '$lte'
                    ): labels[i + 1]
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'total_value': {'$sum': '$value'}
            }
        }
    ]
    return pipeline


def get_dataset(labels, end_time):
    """
    Возвращает датасет выплат по периодам.
    """
    dataset = []
    if labels[-1] <= end_time:
        labels.append(end_time)
    for i in range(len(labels) - 1):
        pipeline = get_pipeline(labels, i)
        result = next(collection.aggregate(pipeline), {'total_value': 0})
        result = result['total_value']
        dataset.append(result)
    return dataset


async def process_message(message: Message) -> str:
    """
    Обработка сообщения.
    """
    try:
        message_text: str | None = message.text
        input_data: dict = json.loads(message_text)
    except Exception:
        resp_message: str = 'Структура сообщения не соответствует формату JSON.'
        return resp_message
    try:
        group_type, start_time, end_time = get_request_data(
            input_data
        )
    except Exception as e:
        return f'Некорректные данные в запросе: {e}'
    labels = get_labels(start_time, end_time, group_type)
    text_labels = []
    for label in labels:
        text_label = label.strftime('%Y-%m-%dT%H:%M:%S')
        text_labels.append(text_label)
    dataset = get_dataset(labels, end_time)
    resp_message = json.dumps(
        {
            "dataset": dataset,
            "labels": text_labels
        }
    )
    return resp_message

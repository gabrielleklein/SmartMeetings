from abc import abstractmethod
from datetime import datetime
import json
from math import ceil
from typing import List, Optional, Union, Dict
from urllib.parse import quote

from slacktastic.exceptions import ValidationError
from slacktastic.constants import (
    BASE_URL,
    BACKGROUND_COLOR_DEFAULTS,
    FOOD_LABEL_OPTIONS
)


class Base:
    @abstractmethod
    def to_slack(self):
        pass


class Attachment(Base):
    def __init__(
            self,
            title: Optional[str] = None,
            title_link: Optional[str] = None,
            pretext: Optional[str] = None,
            text: Optional[str] = None,
            footer: Optional[str] = None,
            footer_icon: Optional[str] = None,
            color: Optional[str] = None,
            fields: Optional[List['Field']] = None,
            formatting: str = 'mrkdwn',
            image_url: Optional[str] = None,
            thumb_url: Optional[str] = None,
            date_time: Optional[datetime] = None
    ):
        if all(not value for value in [title, text, fields]):
            raise ValidationError(
                'Either `title`, `text` or `fields` required')
        self.title = title
        self.title_link = title_link
        self.pretext = pretext
        self.text = text
        self.footer = footer
        self.footer_icon = footer_icon
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.date_time = date_time
        self.color = color
        self.fields = fields
        self.formatting = formatting

        if isinstance(fields, list):
            self.fields = fields
        else:
            self.fields = list()

    def to_slack(self):
        return {
            'title': self.title,
            'title_link': self.title_link,
            'pretext': self.pretext,
            'text': self.text,
            'footer': self.footer,
            'footer_icon': self.footer_icon,
            'image_url': self.image_url,
            'thumb_url': self.thumb_url,
            'ts': self.date_time.timestamp() if self.date_time else None,
            'color': self.color,
            'fields': [field.to_slack() for field in self.fields],
            'type': self.formatting,
        }


class Field:
    def __init__(
            self,
            title: str,
            value: Union[str, int, float, bool],
            short: Optional[bool] = True
    ):
        self.title = title
        self.value = value
        self.short = short

    def to_slack(self):
        return {
            'title': self.title,
            'value': self.value,
            'short': self.short
        }


class Diagram(Attachment):
    diagram_type = None
    options = {}

    def __init__(
            self,
            title: str,
            data: Dict,
            color: Optional[str] = None,
    ):
        self.data = data

        super().__init__(
            title=title,
            color=color,
        )

    def set_options(self, options: Dict):
        self.options = options

    def to_slack(self):
        self._set_image_urls()
        return super().to_slack()

    @abstractmethod
    def _validate_data(self, *args, **kwargs):
        pass

    def _set_image_urls(self):
        payload = {
            'type': self.diagram_type,
            'data': self.data,
            'options': self.options if self.options else {}
        }

        parameters = f"?c={quote(json.dumps(payload))}"
        url = BASE_URL + parameters
        self.image_url = url
        self.thumb_url = url


class Graph(Diagram):
    def __init__(
            self,
            title: str,
            labels: List,
            data: Dict,
            color: Optional[str] = None,
    ):
        self.data = data
        self.labels = labels
        self._validate_data()
        self.background_colors = BACKGROUND_COLOR_DEFAULTS
        self.data = self._format_data(BACKGROUND_COLOR_DEFAULTS)

        super().__init__(
            title=title,
            data=self.data,
            color=color
        )

    def set_background_colors(self, colors: List[str]):
        self.data = self._format_data(colors)

    def _format_data(self, colors: List):
        formatted_data = {
            'labels': self.labels,
            'datasets': []
        }

        bg_colors = iter(colors)
        for label, values in self.data.items():
            try:
                background = next(bg_colors)
            except StopIteration:
                bg_colors = iter(BACKGROUND_COLOR_DEFAULTS)
                background = next(bg_colors)

            dataset = self._format_dataset(label, values, background)
            formatted_data['datasets'].append(dataset)
        return formatted_data

    @staticmethod
    def _format_dataset(
            label: str,
            values: List[Union[int, float]],
            background: str):
        return {
            'label': label,
            'data': values,
            'backgroundColor': background,
        }

    def _validate_data(self):
        label_len = len(self.labels)
        for key, values in self.data.items():
            if label_len != len(values):
                raise ValidationError(
                    f'Labels and values not the same size for "{key}"'
                )


class RadialGauge(Diagram):
    diagram_type = 'radialGauge'

    def __init__(
            self,
            title: str,
            percentage: Union[str, int, float],
            radial_color: Optional[str] = None,
            color: Optional[str] = None,
    ):
        self._validate_data(percentage)
        data = self._format_data(percentage, radial_color)
        super().__init__(title, data, color)

    @staticmethod
    def _format_data(
            percentage: Union[int, float, str],
            radial_color: Optional[str] = None
    ):
        return {
            'datasets': [
                {
                    'data': [percentage],
                    'backgroundColor': radial_color
                }
            ]
        }

    @staticmethod
    def _validate_data(
            percentage: Union[str, int, float]
    ):
        try:
            percentage = int(percentage)
        except ValueError:
            raise ValidationError('Percentage not a number')

        if not (0 <= percentage <= 100):
            raise ValidationError(
                'Invalid percentage: not between 0 and 100')


class BarChart(Graph):
    diagram_type = 'bar'

    def __init__(
            self,
            title: str,
            labels: List,
            data: Dict,
            color: Optional[str] = None,
    ):
        self.data = data
        super().__init__(title, labels, data, color)


class LineChart(Graph):
    diagram_type = 'line'

    def __init__(
            self,
            title: str,
            labels: List,
            data: Dict,
            color: Optional[str] = None,
    ):
        super().__init__(title, labels, data, color)


class RadarChart(Graph):
    diagram_type = 'radar'

    def __init__(
            self,
            title: str,
            labels: List,
            data: Dict,
            color: Optional[str] = None,
    ):
        super().__init__(title, labels, data, color)


class FoodChart(Diagram):
    """
    Wrapper for Pie and Donut charts with special data payload
    """

    def __init__(
            self,
            title: str,
            labels: List,
            values: List,
            color: Optional[str] = None
    ):
        self.options = FOOD_LABEL_OPTIONS
        self.labels = labels
        self.values = values

        self._validate_data()
        self.data = {
            'labels': labels,
            'datasets': [
                {
                    'data': values,
                    'backgroundColor': BACKGROUND_COLOR_DEFAULTS
                }
            ]
        }

        super().__init__(
            title=title,
            data=self.data,
            color=color,
        )

    def set_background_colors(self, colors: List[str]):
        diff = len(self.labels) - len(colors)
        if diff > 0:  # Append the same list x times until we have enough
            parts = ceil(diff / len(colors))
            for _ in range(parts):
                colors = colors + colors

        self.data['datasets'][0]['backgroundColor'] = colors

    def _validate_data(self):
        if len(self.labels) != len(self.values):
            raise ValidationError('Labels and values not the same size')


class PieChart(FoodChart):
    diagram_type = 'pie'

    def __init__(
            self,
            title: str,
            labels: List,
            values: List,
            color: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            labels=labels,
            values=values,
            color=color
        )


class OuterPieChart(FoodChart):
    diagram_type = 'outlabeledPie'

    def __init__(
            self,
            title: str,
            labels: List,
            values: List,
            color: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            labels=labels,
            values=values,
            color=color
        )
        self.set_options(
            {
                "plugins": {
                    "legend": False,
                    "outlabels": {
                        "text": "%l %p",
                        "color": "white",
                        "stretch": 35,
                        "font": {
                            "resizable": True,
                            "minSize": 12,
                            "maxSize": 18
                        }
                    }
                }
            }
        )


class DonutChart(FoodChart):
    diagram_type = 'doughnut'

    def __init__(
            self,
            title: str,
            labels: List,
            values: List,
            color: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            labels=labels,
            values=values,
            color=color,
        )


class Message(Base):
    def __init__(
            self,
            text: Optional[str] = None,
            attachments: List[Optional[Attachment]] = None
    ):
        if all(not value for value in [text, attachments]):
            raise ValidationError('Either `text` or `attachments` required')

        self.text = text
        if isinstance(attachments, list):
            self.attachments = attachments
        else:
            self.attachments = list()

    def to_slack(self):
        return {
            'text': self.text,
            'attachments': [
                attachment.to_slack() for attachment in self.attachments
            ]
        }

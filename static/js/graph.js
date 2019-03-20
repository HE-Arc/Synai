/**
 * Pie chart
 */
class PieChart {
    constructor(id, data_headers, data, text, subtext="")
    {
        this.id = id;
        this.data_headers = data_headers;
        this.data = data;
        this.text = text;
        this.chart = echarts.init(document.getElementById(this.id));
        this.chart.setOption(this.options);
    }

    get options()
    {
        let title = {
            'text': this.text,
            'subtext': this.subtext,
            'left': 'center',
        };

        let tooltip = {
            'trigger': 'item',
            'formatter': "{b} : </br> {d}%"
        };

        let series = [{
            'type': 'pie',
            'radius': '55%',
            'center': ['50%', '60%'],
            'data': this.series_data,
            'itemStyle': {
                'emphasis': {
                    'shadowBlur': 10,
                    'shadowOffsetX': 0,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            }
        }];
        return {'title': title, 'series': series, 'tooltip': tooltip}
    }

    get series_data()
    {
        let pie_data = []
        if (this.data.length === this.data_headers.length)
        {
            for (let i = 0; i < this.data.length; i++)
            {
                pie_data.push({'value': this.data[i], 'name': this.data_headers[i]})
            }
        }
        return pie_data;
    }
}

/**
 * Bar chart
 */
class BarChart {
    constructor(id, data_headers, data, text, subtext="")
    {
        this.id = id;
        this.data_headers = data_headers;
        this.data = data;
        this.text = text;
        this.chart = echarts.init(document.getElementById(this.id));
        this.chart.setOption(this.options);
    }

    get options()
    {
        let title = {
            'text': this.text,
            'subtext': this.subtext,
            'left': 'center'
        };

        let tooltip = {
            'showContent': true,
            'backgroundColor': 'rgba(245, 245, 245, 0.8)',
            'borderWidth': 1,
            'borderColor': '#ccc',
            'padding': 10,
            'textStyle': {
                color: '#000'
            },
        };

        let legend = {
            'data': ['Audio Features'],
            'left': 'left',
        };

        let xAxis = {
            'data': this.data_headers
        };

        let yAxis = {}

        let series = [{
            'type': 'bar',
            'name': 'Audio Features',
            'data': this.data,
        }];
        return {'title': title, 'xAxis': xAxis, 'yAxis': yAxis, 'series': series, 'tooltip': tooltip}
    }
}



/**
 * Radar chart
 */
class RadarChart {
    constructor(id, data_headers, data, text, max_values=[1,1,1,1,1,1,1,10])
    {
        this.id = id;
        this.data_headers = data_headers;
        this.data = data;
        this.text = text;
        this.max_values = max_values;
        this.chart = echarts.init(document.getElementById(this.id));
        this.chart.setOption(this.options);
    }

    get options()
    {
        let title = {
            'text': this.text,
            'subtext': this.subtext,
            'left': 'center'
        };

        let legend = {
            'data': ['Audio Features'],
            'left': 'left',
        };

        let tooltip = {};

        let radar = {
            'name': {
                'textStyle': {
                    'color': 'rgb(238, 197, 102)'
                }
            },
            'shape': 'circle',
            'indicator': this.indicator_data
        };

        let series = [{
            'name': 'Audio Features',
            'type': 'radar',
            'data': [
                {
                    'value': this.data,
                    'name': 'Audio Features'
                }]
        }];
        return {'title': title, 'tooltip': tooltip, 'radar': radar, 'series': series}
    }

    get indicator_data()
    {
        let indicator = []
        if (this.data_headers.length === this.max_values.length)
        {
            for (let i = 0; i < this.data_headers.length; i++)
            {
                indicator.push({'name': this.data_headers[i], 'max': this.max_values[i]})
            }
        }
        return indicator;
    }
}
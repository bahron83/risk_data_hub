import React, { Component } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, Cell, CartesianGrid, Tooltip, Legend } from 'recharts';
import ChartTooltip from './ChartTooltip';

class SChart extends Component {           
    render () {        
        const { riskEvent, data } = this.props;                
        const dataKey = data[0]['dataKey'];
        return (
          <ScatterChart width={500} height={400} margin={{top: 20, right: 0, bottom: 20, left: 0}}>
            <XAxis domain={[1870, 'auto']} dataKey={'year'} type="number" name='Year' unit=''/>
            <YAxis dataKey={dataKey} type="number" name={dataKey} unit=''/>
            <CartesianGrid />
            <Scatter onClick={this.handleClick.bind(this)} data={data} name='Events'>
                {data.map((entry, index) => {
                    const active = entry.event_id === riskEvent.event_id;
                    return (
                        <Cell cursor="pointer" stroke={active ? '#2c689c' : '#ffffff'} strokeWidth={active ? 2 : 1}fill={active ? '#ff8f31' : '#2c689c'} key={`cell-${index}`}/>);
                })
                }
            </Scatter>
            <Tooltip cursor={{strokeDasharray: '3 3'}}/>
        </ScatterChart>
      );
    }

    handleClick(e) {
        const { selectEvent } = this.props;                
        selectEvent(e);
    }
}

export default SChart;
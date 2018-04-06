import React, { Component } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, Cell, CartesianGrid, Tooltip, Legend } from 'recharts';
import ChartTooltip from './ChartTooltip';

class SChart extends Component {           
    shouldComponentUpdate(nextProps, nextState) {
        const { riskEvent: ev, loc } = this.props;
        const { riskEvent: nextEv, loc: nextLoc } = nextProps;
        
        if(ev.event_id !== nextEv.event_id || loc !== nextLoc)
            return true;

        return false;
    } 
    
    render () {        
        const { riskEvent, data, selectEvent } = this.props;                
        const dataKey = data[0]['data_key'];
        return (
          <ScatterChart width={500} height={400} margin={{top: 20, right: 0, bottom: 20, left: 0}}>
            <XAxis domain={[1870, 'auto']} dataKey={'year'} type="number" name='Year' unit=''/>
            <YAxis dataKey={dataKey} type="number" name={dataKey} unit=''/>
            <CartesianGrid />
            <Scatter onClick={selectEvent} data={data} name='Events'>
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
}

export default SChart;
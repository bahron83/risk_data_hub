import React, { Component } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, Cell, CartesianGrid, Tooltip, Legend } from 'recharts';
import ChartTooltip from './ChartTooltip';

class SChart extends Component {           
    shouldComponentUpdate(nextProps, nextState) {
        const { selectedEventIds: ev, fullContext } = this.props;
        const { loc } = fullContext;
        const { selectedEventIds: nextEv, loc: nextLoc } = nextProps;
        
        if(JSON.stringify(ev) !== JSON.stringify(nextEv) || loc !== nextLoc)
            return true;

        return false;
    } 
    
    render () {        
        const { selectedEventIds, data, unitOfMeasure } = this.props;         
        if(data.length == 0)
            return null;           
        const dataKey = data[0]['data_key'];
        return (
          <ScatterChart width={500} height={400} margin={{top: 20, right: 0, bottom: 20, left: 0}}>
            <XAxis domain={['auto', 'auto']} dataKey={'year'} type="number" name='Year' unit=''/>
            <YAxis dataKey={dataKey} type="number" name={dataKey} unit={unitOfMeasure}/>
            <CartesianGrid />
            <Scatter onClick={this.handleClick.bind(this)} data={data} name='Events'>
                {data.map((entry, index) => {
                    const active = selectedEventIds.includes(entry.event_id);
                    return (
                        <Cell cursor="pointer" stroke={active ? '#2c689c' : '#ffffff'} strokeWidth={active ? 2 : 1}fill={active ? '#ff8f31' : '#2c689c'} key={`cell-${index}`}/>);
                })
                }
            </Scatter>
            <Tooltip cursor={{strokeDasharray: '3 3'}}/>
        </ScatterChart>
      );
    }
    
    handleClick(event) {
        const { selectEvent, selectedEventIds } = this.props;        
        const active = selectedEventIds.includes(event.event_id);        
        selectEvent([event.event_id], !active, event.iso2);
    }
}

export default SChart;
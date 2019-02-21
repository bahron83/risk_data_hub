import React, { Component } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, Cell, CartesianGrid, Tooltip, Legend } from 'recharts';
import moment from 'moment';
import SChartTooltip from './SChartTooltip';

class SChart extends Component {           
    shouldComponentUpdate(nextProps, nextState) {        
        const { selectedEventIds: ev, fullContext, data } = this.props;
        const { loc } = fullContext;
        const { selectedEventIds: nextEv, data: nextData } = nextProps;
        const nextLoc = nextProps && nextProps.fullContext && nextProps.fullContext.loc;        
        
        if(JSON.stringify(ev) !== JSON.stringify(nextEv) || loc !== nextLoc || JSON.stringify(data) !== JSON.stringify(nextData))
            return true;

        return false;
    } 
    
    render () {        
        const { selectedEventIds, data, unitOfMeasure } = this.props; 
        //console.log('scatter chart', data);
        if(data.length == 0)
            return null;           
        const dataKey = data[0] && data[0].dataKey;        
        return (
          <ScatterChart width={500} height={400} margin={{top: 20, right: 0, bottom: 20, left: 0}}>
            <XAxis 
                dataKey='timestamp'
                domain={['auto', 'auto']} 
                name='Begin Date' 
                tickFormatter={(unixTime) => moment(unixTime).format('YYYY-MM-DD')}
                type="number" 
                />
            <YAxis dataKey='value' type='number' name={dataKey} unit={unitOfMeasure}/>
            <CartesianGrid />
            <Scatter onClick={this.handleClick.bind(this)} data={data} name='Events'>
                {data.map((entry, index) => {
                    const active = selectedEventIds.includes(entry.id);
                    return (
                        <Cell cursor="pointer" stroke={active ? '#2c689c' : '#ffffff'} strokeWidth={active ? 2 : 1}fill={active ? '#ff8f31' : '#2c689c'} key={`cell-${index}`}/>);
                })
                }
            </Scatter>
            <Tooltip content={<SChartTooltip xAxisUnit={unitOfMeasure} />} />
        </ScatterChart>
      );
    }
    
    handleClick(event) {
        const { selectEvent, selectedEventIds } = this.props;        
        const active = selectedEventIds.includes(event.id);        
        selectEvent([event.id], !active, event.iso2);
    }
}

export default SChart;
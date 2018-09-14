import React, { Component } from 'react';
import { BarChart, Bar, XAxis, Cell, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import ChartTooltip from "./ChartTooltip";

class EventCountryChart extends Component {    
    getChartData() {         
        const { data } = this.props; 
        if(data) {
            return (
                data.map(v => {
                    return {'name': v[0], 'value': parseFloat(v[3], 10)}
                })
            )
        }               
        return [];
    }

    shouldComponentUpdate(nextProps, nextState) {        
        if(this.props.fullContext.loc !== nextProps.fullContext.loc)
            return true;

        return false;
    }  

    render() {          
        const { uOm, skipLabel } = this.props;
        const chartData = this.getChartData(); 
        if(chartData.length > 0) {
            const dimensionX = 'Country';        
            return (          
                <ResponsiveContainer width="100%" height={200}>                    
                    <BarChart width={500} height={200} data={chartData} margin={{top: 20, right: 0, left: 0, bottom: 5}}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name"/>
                        <YAxis/> 
                        <Tooltip content={<ChartTooltip xAxisLabel={dimensionX} xAxisUnit='' uOm={uOm} skipLabel={skipLabel}/>}/>
                        <Bar dataKey="value" onClick={this.handleClick.bind(this)}>                    
                            {chartData.map((entry,index) => {                            
                                const active = entry.name === this.props.fullContext.loc;
                                return(
                                    <Cell cursor="pointer" stroke={"#ff8f31"} strokeWidth={active ? 2 : 0} fill={active ? '#ff8f31' : '#2c689c'} key={`cell-${index}`}/>);                            
                            })}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>)
        }
        return null;
    }

    handleClick(item, index) {        
        const { zoomInOut, contextUrl, fullContext } = this.props;        
        const dataHref = `${contextUrl}/risks/data_extraction/reg/${fullContext.reg}/loc/${item.name}/`;
        const geomHref = `${contextUrl}/risks/data_extraction/reg/${fullContext.reg}/geom/${item.name}/`;
        zoomInOut(dataHref, geomHref);
    }

    formatYTiks(v) {
        return v.toLocaleString();
    }

    formatXTiks(v) {
        return !isNaN(v) && parseFloat(v).toLocaleString() || v;
    }
}

export default EventCountryChart;

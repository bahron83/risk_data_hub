import React, { Component } from 'react';
import { BarChart, Bar, XAxis, Cell, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import ChartTooltip from "./ChartTooltip";

class EventCountryChart extends Component {    
    getChartData() {         
        const { data } = this.props;                
        return (
            data.map(v => {
                return {'name': v[0], 'value': parseFloat(v[3], 10)}
            })
        );     
    }

    shouldComponentUpdate(nextProps, nextState) {
        if(this.props.loc !== nextProps.loc)
            return true;

        return false;
    }  

    render() {          
        const chartData = this.getChartData();        
        const dimensionX = 'Country';        
        return (          
            <ResponsiveContainer width="100%" height={200}>
                <BarChart width={500} height={200} data={chartData} margin={{top: 20, right: 0, left: 0, bottom: 5}}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name"/>
                    <YAxis/> 
                    <Tooltip/>                
                    <Bar dataKey="value" onClick={this.handleClick.bind(this)}>                    
                        {chartData.map((entry,index) => {                            
                            const active = entry.name === this.props.loc;
                            return(
                                <Cell cursor="pointer" stroke={"#ff8f31"} strokeWidth={active ? 2 : 0} fill={active ? '#ff8f31' : '#2c689c'} key={`cell-${index}`}/>);                            
                        })}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>);
    }

    handleClick(item, index) {        
        const { zoomInOut } = this.props;
        const dataHref = `/risks/data_extraction/loc/${item.name}/`;
        const geomHref = `/risks/data_extraction/geom/${item.name}/`;
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

import React, { Component } from 'react';
import { BarChart, Bar, XAxis, Cell, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import ChartTooltip from "./ChartTooltip";

class EventCountryChart extends Component {    
    getChartData() {         
        const { data, currentAdminUnits, groupEventAnalysisData } = this.props;        
        return groupEventAnalysisData(data, currentAdminUnits);
    }

    /*shouldComponentUpdate(nextProps, nextState) {        
        const { selectedEventIds: ev, fullContext, data } = this.props;
        const { loc } = fullContext;
        const { selectedEventIds: nextEv, data: nextData } = nextProps;
        const nextLoc = nextProps && nextProps.fullContext && nextProps.fullContext.loc;        
        
        if(JSON.stringify(ev) !== JSON.stringify(nextEv) || loc !== nextLoc || JSON.stringify(data) !== JSON.stringify(nextData))
            return true;

        return false;
    }*/ 

    render() {  
        //console.log('event country chart', this.props);
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

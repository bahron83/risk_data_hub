import React, { Component } from 'react';
import { ComposedChart, BarChart, Bar, Line, XAxis, Cell, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

class SendaiCountryChart extends Component {
    getChartData() {
        const { data } = this.props;
        const { sendaiValues } = data;        
        const values = [...sendaiValues.slice(1, sendaiValues.length)];
        
        if(values) {              
            return (
                values.map(v => {                    
                    const value = this.round(parseFloat(v[1]), 2);
                    const baseline = this.getRefValue();
                    const percentDiff = this.round((value - baseline) / baseline * 100, 2);
                    return {'name': v[0], 'value': value, 'baseline': baseline, 'percentDiff': percentDiff}
                })
            )
        }
        return [];
    }

    round(value, decimals) {
        return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
    }

    getRefValue() {
        const { data } = this.props;
        const { sendaiValues } = data;        
        return sendaiValues && sendaiValues.length > 0 ? this.round(parseFloat(sendaiValues[0][1]), 2) : null;
    }

    getSendaiIndicator() {
        const { dim, data } = this.props;
        const { dimensions } = data;
        const { values } = dimensions[dim.dim1];
        const dimension = values[dim.dim1];        
        return dimensions[dim.dim1]['layers'][dimension]['sendaiTarget'];
    }

    renderTooltip(data) {        
        if(data.active) {
            const payload = data && data.payload && data.payload[0] && data.payload[0].payload;
            const value = payload && payload.value;
            const baseline = payload && payload.baseline;
            const percentDiff = payload && payload.percentDiff;            
            const color = percentDiff > 0 ? "#ff0000" : "#00ff00";            
            return (
                <div className="disaster-chart-tooltip">
                    <p className="disaster-chart-tooltip-values">{`Value: ${value}`}</p>
                    <p className="disaster-chart-tooltip-values">{`Baseline: ${baseline}`}</p>
                    <p style={{color:color}} className="disaster-chart-tooltip-values">{`Difference: ${percentDiff} %`}</p>
                </div>    
            )
        }
        return null;        
    }
    
    render() {                     
        const chartData = this.getChartData();
        const sendaiIndicator = this.getSendaiIndicator();                
        if(sendaiIndicator) { 
            return (
                <div>
                    <p>{`Indicator ${sendaiIndicator.code}: ${sendaiIndicator.description}`}</p>
                    <p>Reference value for years 2005/2015: <span>{this.getRefValue()}</span></p>
                    {chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={200}>                    
                            <ComposedChart width={500} height={200} data={chartData} margin={{top: 20, right: 0, left: 0, bottom: 5}}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name"/>
                                <YAxis/> 
                                <Tooltip content={this.renderTooltip}/>                
                                <Bar dataKey="value">                    
                                    {chartData.map((entry,index) => {                                                                
                                        return(
                                            <Cell cursor="pointer" stroke={"#ff8f31"} strokeWidth={1} fill={"#2c689c"} key={`cell-${index}`}/>);                            
                                    })}
                                </Bar>
                                <Line type="monotone" dataKey="baseline" stroke="#ff7300"/>                            
                            </ComposedChart>
                        </ResponsiveContainer>
                        ) : null                
                    }
                </div>                
        )}
        return (
            <div>
                No data available
            </div>
        );                
    }    
}

export default SendaiCountryChart;
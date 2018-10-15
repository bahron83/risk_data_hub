import React, { Component } from 'react';
import { ComposedChart, Bar, Line, XAxis, Cell, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';


class SendaiCountryChart extends Component {
    getChartData() {
        const { data, round } = this.props;
        const { sendaiValues } = data;        
        const values = [...sendaiValues.slice(1, sendaiValues.length)];        
        if(values) {              
            return (
                values.map(v => {                                        
                    const value = round(v[1]);                    
                    const baseline = this.getRefValue();
                    const percentDiff = round((value - baseline) / baseline * 100);
                    return {'name': v[0], 'value': value, 'baseline': baseline, 'percentDiff': percentDiff}
                })
            )
        }
        return [];
    }    

    getRefValue() {
        const { data } = this.props;
        const { sendaiValues } = data;        
        return sendaiValues && sendaiValues.length > 0 ? sendaiValues[0][1] : null;
    }

    getBaselineUnit() {        
        const values = this.props && this.props.data && this.props.data.sendaiValues;
        if(values) {
            return values[0][2];
        }
        return '';
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
                    <p className="disaster-chart-tooltip-values">{`Value: ${value.toLocaleString()}`}</p>
                    <p className="disaster-chart-tooltip-values">{`Baseline: ${baseline.toLocaleString()}`}</p>
                    <p style={{color:color}} className="disaster-chart-tooltip-values">{`Difference: ${percentDiff} %`}</p>
                </div>    
            )
        }
        return null;        
    }
    
    render() {                             
        const sendaiIndicator = this.getSendaiIndicator();        
        if(sendaiIndicator) { 
            const chartData = this.getChartData();
            return (
                <div>
                    <p>{`Indicator ${sendaiIndicator.code}: ${sendaiIndicator.description}`}</p>
                    <p>Reference value for years 2005/2015: <span>{`${this.getRefValue().toLocaleString()} ${this.getBaselineUnit()}`}</span></p>
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
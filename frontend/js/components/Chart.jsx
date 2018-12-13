import React, { Component } from 'react';
import { BarChart, Bar, XAxis, Cell, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import ChartTooltip from './ChartTooltip';

const CustomizedYLable = (props) => {
    const {x, y, lab} = props;
    return (
        <g className="recharts-cartesian-axis-label">
        <text x={x} y={y} dy={-10} dx={56} textAnchor="middle" fill="#666" transform="rotate(0)" className="recharts-text">{lab}</text>
        </g>
        );
};

class Chart extends Component {    
    shouldComponentUpdate(nextProps, nextState) {        
        if((this.props.dim.dim1Idx !== nextProps.dim.dim1Idx) || (this.props.dim.dim2Idx !== nextProps.dim.dim2Idx) || (this.props.val !== nextProps.val) || (this.props.values !== nextProps.values))
            return true;

        return false;
    } 
    
    getChartData() {
        const { dim, values, val } = this.props;        
        return values.filter((d) => d[dim.dim1] === val ).map((v) => {return {"name": v[dim.dim2], "value": parseFloat(v[2], 10)}; });
    }

    render() {        
        const { dim, dimension, uOm, skipLabel, selectRP } = this.props;        
        const chartData = this.getChartData();
        /*const colors = chromaJs.scale('OrRd').colors(chartData.length);*/
        return (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart width={500} height={200} data={chartData}
                margin={{top: 20, right: 30, left: 30, bottom: 5}}>
                <XAxis dataKey="name" tickFormatter={this.formatXTiks}/>
                <Tooltip content={<ChartTooltip xAxisLabel={dimension[dim.dim2].name} xAxisUnit={dimension[dim.dim2].unit} uOm={uOm} skipLabel={skipLabel}/>}/>
                <YAxis label={<CustomizedYLable lab={uOm}/>} interval="preserveStart" tickFormatter={this.formatYTiks}/>
                <CartesianGrid strokeDasharray="3 3" />
                <Bar dataKey="value" onClick={selectRP}>
                    {chartData.map((entry, index) => {
                        const active = index === dim.dim2Idx;
                        return (
                            <Cell cursor="pointer" stroke={"#ff8f31"} strokeWidth={active ? 2 : 0}fill={active ? '#2c689c' : '#ff8f31'} key={`cell-${index}`}/>);
                    })
                    }
                </Bar>
            </BarChart></ResponsiveContainer>);
    }    

    formatYTiks(v) {
        return v.toLocaleString();
    }

    formatXTiks(v) {
        return !isNaN(v) && parseFloat(v).toLocaleString() || v;
    }
    
};

export default Chart;
const React = require('react');
const {BarChart, Bar, XAxis, Cell, YAxis, Tooltip, CartesianGrid, ResponsiveContainer} = require('recharts');
const ChartTooltip = require("./ChartTooltip");
const _ = require('lodash');

const EventCountryChart = React.createClass({
    propTypes: {
        values: React.PropTypes.object,
        zoomInOut: React.PropTypes.func,
        fullContext: React.PropTypes.object      
    },
    getDefaultProps() {
        return {
        };
    },
    getChartData() {
        const { values } = this.props;
        let dataGrouped = [];        
        
        //Object.entries(values).map(([k, v]) => 
        _.map(values, v => {
            const index = dataGrouped.findIndex(e => e.name == v[0]);
            const value = parseFloat(v[3], 10);
            if(index > -1)
            dataGrouped[index]['value'] += value;
            else
            dataGrouped.push({"name": v[0], "value": value});
        });
        
        dataGrouped = _.orderBy(dataGrouped, 'value', 'desc');        
        return dataGrouped;        
    },
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
                    <Bar dataKey="value" onClick={this.handleClick}>                    
                        {chartData.map((entry,index) => {
                            const ctx = this.props.fullContext;
                            const active = entry.name === ctx.loc;
                            return(
                                <Cell cursor="pointer" stroke={"#ff8f31"} strokeWidth={active ? 2 : 0}fill={active ? '#ff8f31' : '#2c689c'} key={`cell-${index}`}/>);                            
                        })}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>);
    },
    handleClick(item, index) {
        const dataHref = '/risks/data_extraction/loc/' + item.name + '/';
        const geomHref = '/risks/data_extraction/geom/' + item.name + '/';
        this.props.zoomInOut(dataHref, geomHref);
    },
    formatYTiks(v) {
        return v.toLocaleString();
    },
    formatXTiks(v) {
        return !isNaN(v) && parseFloat(v).toLocaleString() || v;
    }
});

module.exports = EventCountryChart;

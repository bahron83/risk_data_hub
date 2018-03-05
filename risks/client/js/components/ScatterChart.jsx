const React = require('react');
const {ScatterChart, Scatter, XAxis, YAxis, Cell, CartesianGrid, Tooltip, Legend} = require('recharts');
const ChartTooltip = require("./ChartTooltip");

const data = [{x: 100, y: 200, z: 200}, {x: 120, y: 100, z: 260},
    {x: 170, y: 300, z: 400}, {x: 140, y: 250, z: 280},
    {x: 150, y: 400, z: 500}, {x: 110, y: 280, z: 200}]

const SChart = React.createClass({
    propTypes: {
        riskEvent: React.PropTypes.object,
        events: React.PropTypes.array,        
        setEventIdx: React.PropTypes.func, 
        getEventData: React.PropTypes.func
    },
    getDefaultProps() {
        return {
        };
    },
    getComponentData() {
        const {events} = this.props;                 
        return events;
    },   
    render () {
        const eventData = this.getComponentData();        
        const {riskEvent} = this.props;
        const list = [];
        eventData.forEach(function(obj){
            var newObj = obj.fields;
            newObj['event_id'] = obj.pk
            list.push(newObj);
        }); 

        //console.log(list);

        return (
          <ScatterChart width={400} height={400} margin={{top: 20, right: 20, bottom: 20, left: 20}}>
            <XAxis domain={[1870, 'auto']} dataKey={'year'} type="number" name='Year' unit=''/>
            <YAxis dataKey={'people_affected'} type="number" name='People Affected' unit=''/>
            <CartesianGrid />
            <Scatter onClick={this.handleClick} data={list} name='Events'>
                {list.map((entry, index) => {
                    const active = entry.event_id === riskEvent.eventid;
                    return (
                        <Cell cursor="pointer" stroke={active ? '#2c689c' : '#ffffff'} strokeWidth={active ? 2 : 1}fill={active ? '#ff8f31' : '#2c689c'} key={`cell-${index}`}/>);
                })
                }
            </Scatter>
            <Tooltip cursor={{strokeDasharray: '3 3'}}/>
        </ScatterChart>
      );
    },
    handleClick(item, index) {
        //console.log(item);
        const nuts3 = item.nuts3.split(';');
        this.props.setEventIdx('eventid', item.event_id, 'nuts3', nuts3);
        this.props.getEventData('/risks/data_extraction/loc/'+item.iso2+'/ht/'+item.hazard_type+'/evt/'+item.event_id+'/');
    }
});

module.exports = SChart;
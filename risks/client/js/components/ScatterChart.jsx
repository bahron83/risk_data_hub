const React = require('react');
const {ScatterChart, Scatter, XAxis, YAxis, Cell, CartesianGrid, Tooltip, Legend} = require('recharts');
const ChartTooltip = require("./ChartTooltip");

const SChart = React.createClass({
    propTypes: {
        riskEvent: React.PropTypes.object,
        events: React.PropTypes.array,
        fullContext: React.PropTypes.object,
        setEventIdx: React.PropTypes.func, 
        getEventData: React.PropTypes.func
    },
    getInitialState: function() {
        return {selectedEvent: null, loc: null};
    },
    getDefaultProps() {
        return {
        };
    },
    getComponentData() {
        const {events} = this.props;                 
        const list = [];
        events.forEach(function(obj){
            var newObj = obj.fields;
            newObj['event_id'] = obj.pk
            list.push(newObj);
        });
        return list;
    },   
    render () {
        const list = this.getComponentData();        
        const {riskEvent} = this.props;                

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
    componentDidMount() {               
        this.componentDidUpdate();
    },
    componentDidUpdate() {                
        /*pre-select most recent event*/
        const {riskEvent, fullContext} = this.props;        
        if((this.state.selectedEvent == null || this.state.loc != fullContext.loc) && fullContext.adm_level > 0) {
            const list = this.getComponentData();
            if(list.length > 0) {
                const selEvent = list[0];
                this.setState({selectedEvent: selEvent, loc: fullContext.loc});
                this.handleClick(selEvent, 0);
            }
        }
    },
    handleClick(item, index) {
        /*console.log(item);*/
        const nuts3 = item.nuts3.split(';');
        this.props.setEventIdx('eventid', item.event_id, 'nuts3', nuts3);
        this.props.getEventData('/risks/data_extraction/loc/'+item.iso2+'/ht/'+item.hazard_type+'/evt/'+item.event_id+'/');
    }
});

module.exports = SChart;
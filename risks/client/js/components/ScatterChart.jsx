const React = require('react');
const {ScatterChart, Scatter, XAxis, YAxis, Cell, CartesianGrid, Tooltip, Legend} = require('recharts');
const ChartTooltip = require("./ChartTooltip");

const SChart = React.createClass({
    propTypes: {
        riskEvent: React.PropTypes.object,
        events: React.PropTypes.array,
        fullContext: React.PropTypes.object,
        setEventIdx: React.PropTypes.func, 
        getEventData: React.PropTypes.func,
        zoomInOut: React.PropTypes.func,
        zoomJustCalled: React.PropTypes.boolean
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
        return events;
    },   
    render () {
        const events = this.getComponentData();        
        const {riskEvent} = this.props;                
        //console.log(riskEvent);
        return (
          <ScatterChart width={500} height={400} margin={{top: 20, right: 0, bottom: 20, left: 0}}>
            <XAxis domain={[1870, 'auto']} dataKey={'year'} type="number" name='Year' unit=''/>
            <YAxis dataKey={'people_affected'} type="number" name='People Affected' unit=''/>
            <CartesianGrid />
            <Scatter onClick={this.handleClick} data={events} name='Events'>
                {events.map((entry, index) => {
                    const active = entry.event_id === riskEvent.event_id;
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
        const {riskEvent, fullContext, zoomJustCalled} = this.props; 
        /*console.log(fullContext);
        console.log(riskEvent);
        console.log(zoomJustCalled);*/
        if(Object.keys(riskEvent).length === 0 && fullContext.adm_level > 0 && zoomJustCalled == false) {
            const list = this.getComponentData();
            if(list.length > 0) {                
                this.handleClick(list[0]);
            }
        }        
    },
    handleClick(item) {         
        const {fullContext} = this.props;              
        if(fullContext.adm_level == 0) {
            const dataHref = '/risks/data_extraction/loc/' + item.iso2 + '/';
            const geomHref = '/risks/data_extraction/geom/' + item.iso2 + '/';
            this.props.zoomInOut(dataHref, geomHref);            
        }
        else {
            this.props.setEventIdx(item);
            this.props.getEventData('/risks/data_extraction/loc/'+item.iso2+'/ht/'+item.hazard_type+'/evt/'+item.event_id+'/');
        }        
    }
});

module.exports = SChart;
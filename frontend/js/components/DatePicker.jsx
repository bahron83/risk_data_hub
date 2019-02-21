import React from 'react';
import PropTypes from 'prop-types';
import momentPropTypes from 'react-moment-proptypes';
import moment from 'moment';
import omit from 'lodash/omit';
import 'react-dates/initialize';
import { DateRangePicker } from 'react-dates';

import { DateRangePickerPhrases } from 'react-dates/src/defaultPhrases';
import DateRangePickerShape from 'react-dates';
import { START_DATE, END_DATE, HORIZONTAL_ORIENTATION, ANCHOR_LEFT } from 'react-dates/src/constants';
import { isInclusivelyAfterDay } from 'react-dates';

const propTypes = {
  // example props for the demo
  autoFocus: PropTypes.bool,
  autoFocusEndDate: PropTypes.bool,
  stateDateWrapper: PropTypes.func,
  initialStartDate: momentPropTypes.momentObj,
  initialEndDate: momentPropTypes.momentObj,
  startDateId: PropTypes.string,
  endDateId: PropTypes.string,
  setFilters: PropTypes.func,
  fullContext: PropTypes.object,
  loading: PropTypes.bool,

  ...omit(DateRangePickerShape, [
    'startDate',
    'startDateId',
    'endDate',
    'endDateId',
    'onDatesChange',
    'focusedInput',
    'onFocusChange',
  ]),
};

const defaultProps = {
  // example props for the demo
  autoFocus: false,
  autoFocusEndDate: false,
  initialStartDate: null,
  initialEndDate: null,

  // input related props
  startDateId: START_DATE,
  startDatePlaceholderText: 'Start Date',
  endDateId: END_DATE,
  endDatePlaceholderText: 'End Date',
  disabled: false,
  required: false,
  screenReaderInputMessage: '',
  showClearDates: false,
  showDefaultInputIcon: false,
  customInputIcon: null,
  customArrowIcon: null,
  customCloseIcon: null,
  block: false,
  small: false,
  regular: false,

  // calendar presentation and interaction related props
  renderMonthText: null,
  orientation: HORIZONTAL_ORIENTATION,
  anchorDirection: ANCHOR_LEFT,
  horizontalMargin: 0,
  withPortal: false,
  withFullScreenPortal: false,
  initialVisibleMonth: null,
  numberOfMonths: 2,
  keepOpenOnDateSelect: false,
  reopenPickerOnClearDates: false,
  isRTL: false,

  // navigation related props
  navPrev: null,
  navNext: null,
  onPrevMonthClick() {},
  onNextMonthClick() {},
  onClose() {},

  // day presentation and interaction related props
  renderCalendarDay: undefined,
  renderDayContents: null,
  minimumNights: 1,
  enableOutsideDays: false,
  isDayBlocked: () => false,
  //isOutsideRange: day => !isInclusivelyAfterDay(day, moment()),
  isOutsideRange: () => false,
  isDayHighlighted: () => false,

  // internationalization
  displayFormat: () => moment.localeData().longDateFormat('L'),
  monthFormat: 'MMMM YYYY',
  phrases: DateRangePickerPhrases,

  stateDateWrapper: date => date,
};

class DateRangePickerWrapper extends React.Component {
    constructor(props) {
        super(props);

        let focusedInput = null;
        if (props.autoFocus) {
            focusedInput = START_DATE;
        } else if (props.autoFocusEndDate) {
            focusedInput = END_DATE;
        }

        this.state = {
            focusedInput,
            startDate: props.initialStartDate,
            endDate: props.initialEndDate,
        };

        this.onDatesChange = this.onDatesChange.bind(this);
        this.onFocusChange = this.onFocusChange.bind(this);
        this.renderMonthElement = this.renderMonthElement.bind(this);
    }

    onDatesChange({ startDate, endDate }) {
        const { stateDateWrapper } = this.props;
        this.setState({
            startDate: startDate && stateDateWrapper(startDate),
            endDate: endDate && stateDateWrapper(endDate),
        });
    }

    onFocusChange(focusedInput) {
        this.setState({ focusedInput });
    }

    returnYears = () => {
        let years = []
        for(let i = moment().year() - 100; i <= moment().year(); i++) {
            years.push(<option key={`year-${i}`} value={i}>{i}</option>);
        }
        return years;
    }

    renderMonthElement = ({ month, onMonthSelect, onYearSelect }) =>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div>
                <select
                    value={month.month()}
                    onChange={(e) => onMonthSelect(month, e.target.value)}
                >
                    {moment.months().map((label, value) => (
                        <option key={`month-${value}`} value={value}>{label}</option>
                    ))}
                </select>
            </div>
            <div>
                <select value={month.year()} onChange={(e) => onYearSelect(month, e.target.value)}>
                    {this.returnYears()}
                </select>
            </div>
        </div>

    renderResetButton() {    
        const { loading } = this.props;
        return this.state.startDate != null ? <button className="loadAll btn btn-default pull-right" onClick={this.resetFilters.bind(this)}><i className={loading && "icon-spinner fa-spin" || 'fa'}/>{loading && "Loading..." || "Reset filters"}</button> : null;
        }

    renderMainButton() {
        const { setFilters, fullContext } = this.props;
        return (this.state.startDate && this.state.endDate) ? 
            <button 
                className="loadAll btn btn-default pull-right" 
                onClick={() => setFilters(fullContext.full_url, {from: this.state.startDate, to: this.state.endDate})}><i className='fa'
            />Apply Filter</button> : null
    }

    resetFilters(e) {
        const { setFilters, fullContext } = this.props;
        this.setState({ startDate: null, endDate: null });
        setFilters(fullContext.full_url);
    }

    render() {         
        const { focusedInput, startDate, endDate } = this.state;
        const { startDateId, endDateId } = this.props;

        // autoFocus, autoFocusEndDate, initialStartDate and initialEndDate are helper props for the
        // example wrapper but are not props on the SingleDatePicker itself and
        // thus, have to be omitted.
        const props = omit(this.props, [
            'autoFocus',
            'autoFocusEndDate',
            'initialStartDate',
            'initialEndDate',
            'stateDateWrapper',
            'setFilters',
            'fullContext',
            'loading'
        ]);

        return (
        <div>
            <DateRangePicker
                {...props}
                onDatesChange={this.onDatesChange}
                onFocusChange={this.onFocusChange}
                focusedInput={focusedInput}
                startDate={startDate}
                startDateId={startDateId}
                endDate={endDate}
                endDateId={endDateId}
                renderMonthElement={this.renderMonthElement}
            />
            {this.renderResetButton()}
            {this.renderMainButton()}
        </div>
        );
    }
}

DateRangePickerWrapper.propTypes = propTypes;
DateRangePickerWrapper.defaultProps = defaultProps;

export default DateRangePickerWrapper;
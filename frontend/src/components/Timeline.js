// frontend/src/components/Timeline.js

import React, { useEffect, useRef } from 'react';
import axios from 'axios';
import { DataSet, Timeline } from 'vis-timeline/standalone';
import moment from 'moment';

const TimelineComponent = () => {
  const timelineRef = useRef(null);

  useEffect(() => {
    const container = timelineRef.current;
    const items = new DataSet([]);
    const groups = new DataSet([
      { id: 'sound', content: 'Sound Events' },
      { id: 'speech', content: 'Speech Transcriptions' },
    ]);

    const options = {
      stack: false,
      showCurrentTime: true,
      zoomMin: 1000 * 3, // Three seconds
      zoomMax: 1000 * 60 * 60 * 24 * 7, // One week
      type: 'box',
      min: moment().subtract(1, 'day').toDate(),
      max: moment().add(1, 'day').toDate(),
      selectable: true,
      groupOrder: function (a, b) {
        return a.id.localeCompare(b.id);
      },
    };

    const timelineInstance = new Timeline(container, items, groups, options);

    const fetchEvents = async () => {
      try {
        const startTime = moment().subtract(1, 'day').toISOString();
        const endTime = moment().add(1, 'day').toISOString();

        const response = await axios.get('/api/events', {
          params: {
            start_time: startTime,
            end_time: endTime,
          },
        });

        const events = response.data;

        const timelineItems = events.map((event) => ({
          id: event.id,
          content: `<b>${event.label}</b>`,
          start: moment(event.timestamp).toDate(),
          group: event.event_type,
          title: event.confidence !== null ? `Confidence: ${event.confidence}` : '',
          audio_id: event.audio_id,
        }));

        items.clear();
        items.add(timelineItems);

        // Add event listener for audio playback
        timelineInstance.on('select', function (properties) {
          const selectedItem = items.get(properties.items[0]);
          if (selectedItem && selectedItem.audio_id) {
            // Fetch and play audio
            const audio = new Audio(`/api/audio/${selectedItem.audio_id}`);
            audio.play();
          }
        });
      } catch (error) {
        console.error('Error fetching events:', error);
      }
    };

    fetchEvents();

    return () => {
      if (timelineInstance) {
        timelineInstance.destroy();
      }
    };
  }, []);

  return (
    <div>
      <h2>Event Timeline</h2>
      <div ref={timelineRef} style={{ height: '500px' }} />
    </div>
  );
};

export default TimelineComponent;

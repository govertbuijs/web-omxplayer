<div class="path">{{ path or 'Not playing' }}</div>
<div class="name">{{ name or '' }}</div>
<div class="time">{{pos or '00:00:00' }} / {{length or '00:00:00.00' }}</div>
<input type="hidden" id="running" value="{{ running }}">

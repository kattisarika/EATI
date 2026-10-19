"""Browser inactivity logout for Streamlit 1.52+.

Call install_idle_timeout() in the app.py entrypoint before st.navigation(...).run().
The browser tracks activity and navigates to a logout URL after 15 minutes.
"""
import json
import uuid

import streamlit as st

TIMEOUT_MINUTES = 5


def install_idle_timeout():
    # This query parameter is a logout request, not a security credential.
    if st.query_params.get("idle_logout") == "1":
        st.query_params.clear()
        st.session_state.clear()
        st.logout()
        st.stop()

    if not st.user.get("is_logged_in", False):
        # No idle timer on the login screen.
        return

    # The id distinguishes a new login/session from an older browser timer.
    if "idle_timer_session_id" not in st.session_state:
        st.session_state["idle_timer_session_id"] = uuid.uuid4().hex

    session_id = json.dumps(st.session_state["idle_timer_session_id"])
    timeout_ms = TIMEOUT_MINUTES * 60 * 1000

    # Only trusted, constant code and a generated id are inserted here.
    st.html(
        f"""
<script>
(() => {{
  const sessionId = {session_id};
  const timeoutMs = {timeout_ms};
  const storageKey = 'eatiIdleTracker';
  const now = () => Date.now();

  // Repeated Streamlit reruns must not install duplicate event listeners.
  if (window.__eatiIdleTracker?.sessionId === sessionId) return;
  if (window.__eatiIdleTracker?.cleanup) window.__eatiIdleTracker.cleanup();

  let state;
  try {{ state = JSON.parse(sessionStorage.getItem(storageKey) || 'null'); }}
  catch (_) {{ state = null; }}
  if (!state || state.sessionId !== sessionId || !Number.isFinite(state.lastActivity)) {{
    state = {{ sessionId, lastActivity: now() }};
    sessionStorage.setItem(storageKey, JSON.stringify(state));
  }}

  let lastWrite = 0;
  let loggingOut = false;
  function expireIfIdle() {{
    if (loggingOut || now() - state.lastActivity < timeoutMs) return false;
    loggingOut = true;
    sessionStorage.removeItem(storageKey);
    window.location.replace('/?idle_logout=1');
    return true;
  }}
  function markActivity() {{
    if (expireIfIdle()) return;
    const t = now();
    // Throttle writes for frequent mouse movements.
    if (t - lastWrite < 1000) return;
    lastWrite = t;
    state.lastActivity = t;
    sessionStorage.setItem(storageKey, JSON.stringify(state));
  }}
  function onVisibility() {{
    if (!document.hidden) expireIfIdle();
  }}
  const events = ['pointerdown', 'pointermove', 'keydown', 'wheel', 'touchstart'];
  for (const eventName of events) document.addEventListener(eventName, markActivity, {{passive: true}});
  document.addEventListener('visibilitychange', onVisibility);
  window.addEventListener('focus', expireIfIdle);
  const timer = window.setInterval(expireIfIdle, 1000);
  window.__eatiIdleTracker = {{
    sessionId,
    cleanup: () => {{
      window.clearInterval(timer);
      for (const eventName of events) document.removeEventListener(eventName, markActivity);
      document.removeEventListener('visibilitychange', onVisibility);
      window.removeEventListener('focus', expireIfIdle);
    }}
  }};
  expireIfIdle();
}})();
</script>
""",
        unsafe_allow_javascript=True,
    )

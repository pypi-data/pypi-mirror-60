This package contains a replacement for Zope's ``Products.Transience``,
which is typically used to implement Zope's sessions.
While ``Products.Transience`` 
has quite a high risk for ``ConflictError`` if many requests access the
Zope session, the current package should be
responsible only for very few ``ConflictError``\ s, even if every request
accesses the Zope session.

This is achieved by a changed organization of the sessions set.
``Products.Transience`` organizises this set into a list of generations.
If a session is accessed, it is moved into the newest generation
(if not already there). This way, a session access (even
a read only session access) can cause a write and result in
a ``ConflictError``. ``dm.zope.session`` maintains the sessions
in an ``OOBTree`` (which has partial conflict resolution). To support
session timeout, the last access time is maintained on the individual
session object in a data structure with 100 % conflict resolution.
This way, read access to the session should not result in a
``ConflictError``.
To reduce ZODB bloat, the access time is not updated on every access
but employs a limited resolution, by default about 1/8 of the session timeout.

``Products.Transience`` performs an inline cleanup for outdated
sessions. It can do that because its cleanup is very fast (drop the oldest
generation and create a new newest one). ``dm.zope.session``'s
cleanup involves visiting all sessions and check whether they are
outdated. This can be expensive. Therefore, it performs the cleanup
offline - in a separate thread. The cleanup uses very short transactions
to reduce the risk of conflicts.

If you use Zope in a ZEO setup, i.e. serveral Zope processes use
the same ZODB, then only one of the Zope processes will run the
cleanup thread. It may take until the (old) period of this thread
has finished before some configuration changes become effective
(especially ``cleanup_period_sec``). In general, this should not
make a big problem. Should it be problematic in special cases,
you may need to restart this process. You will find its process
id in a lockfile under *clienthome* with a name derived from
the session container path.


**ATTENTION** Like most (server side) session implementations,
``dm.zope.session`` can be vulnerable to denial of service
attacks. It is often not difficult to make the server create
a new session and each session needs resources; an attacker
can try to massively create sessions in order to overload this
kind of resource. ``dm.zope.session`` puts its sessions into a
ZODB which typically uses a file as storage. This kind of resource
usually has a large capacity and therefore is difficult to overload.
However, should an overload happen, the consequences can be severe.
Please read the section `DOS attacks`_ to learn about some
of your options to counter those attacks.


Features
========

``dm.zope.session`` supports the following features.
Corresponding configuration variables are specified in parenthesis.

Maximal session lifetime (``session_max_lifetime_min``)
  This feature allows to limit the maximal lifetime of the session.
  It can be interesting for security reasons: should an
  attacker have been able to hijack a session, he should only
  be able to use it for a limited period.

  In Zope's session architecture, the session id is managed by
  the so called ``browser_id_manager``. It is using a cookie
  to pass the session id between browser and server.
  To be effective, the maximal session lifetime must be combined
  with a limited lifetime for the session id; otherwise, an
  attacker can use the known session id to hijack a followup
  session. In modern Zope versions, the session id is by default
  stored in a (browser) session cookie. In this setup, an attacker
  can hijack followup sessions until the user terminates his
  browser session.

  The maximal session lifetime is controlled via the
  configuration variable ``session_max_lifetime_min``.
  It specifies the maximal lifetime in minutes. A non positive
  value deactivates the feature.

Session inactivity timeout (``session_timeout_min``)
  A session is deleted when is it not used for about
  ``session_timeout_min`` minutes. If ``session_timeout_min``
  has a non positive value, the feature is deactivated.

  The timeout feature is not implemented precisely:
  a session may be deleted slightly before the specified
  inactivity and may live slightly longer than the specified
  timeout. There are two reasons for this:

   1. to avoid ZODB bloat, the session access time is stored
      with limited (usually about 1/8 of the session timeout) resolution.

   2. session inactivation is performed by a periodic cleanup
      process. Nothing happens until the next run of this process.

  The inactivity timeout is an inportant feature for
  sessions implemented by ``Products.Transience``, because
  it typically stores sessions in (precious) RAM. ``dm.zope.session``
  sessions are typically stored in a ``FileStorage`` for
  which early freeing resources is of far less importance.
  However, if you store sensible information in the session,
  you may still want to use this feature for security reasons:
  it forces a potential attacker to keep a hijacked session alive
  for continued exploitation.

Session access time resolution (``session_access_time_resolution_min``)
  This controls whether the session access time
  is updated: an update is suppressed if the last update was
  more recent then the access time resolution.
  ``session_access_time_resolution_min`` specifies an access
  time resolution in minutes. The effective access time
  resolution is the minimum of this resolution and about 1/8
  of the session timeout where non positive values are ignored.
  If both resolutions are non positive, the access time is not
  maintained.

Session target number (``session_target_number``)
  A periodic cleanup tries to keep the number of sessions below
  ``session_target_number`` by deleting the oldest sessions.
  A non positive value for ``session_target_number`` deactivates
  the feature.

Session maximal number (``session_max_number``)
  ``session_max_number`` limits the number of session objects.
  The exception ``dm.zope.session.MaximalSessionNumberExceeded``
  is raised when the limit would be exceeded. A non positive
  value deactivates the feature.

  This option can be used to limit the thread posed
  by `DOS attacks`_.

Periodic session cleanup (``cleanup_period_sec``)
  A periodic cleanup process deletes sessions whose maximal lifetime
  or inactivity timeout is reached. It also deletes the oldest
  sessions to keep the session number below
  the session target number. ``cleanup_period_sec`` specifies
  the period for this process in seconds. If it has a non positive
  value, 10 is used instead.

Events
  For customization purposes, some events are notified. Their
  interfaces are all defined in ``dm.zope.session.interfaces``.
  All events are "object events" with either the session
  or the session container as event object.

  ``ISessionCreatedEvent``
    Notified when a new session object is created.
    Can be used to transfer information from the request to the
    session, e.g. information potentially helpful to detect
    `DOS attacks`_.

  ``IMaximalSessionNumberExceededEvent``
    Notified when the maximal session number is reached.
    Can be used to implement a custom policy to delete
    sessions in such a case in order to let the operation succeed.
    Note, however, that the deletion of the same
    session by concurrent requests leads to an unresolvable
    conflict (only one of those requests will succeed); it is therefore
    advicable to choose the session to be deleted with considerable randomness.

  ``ISessionCleanupEvent``
    Notified during each cleanup round.
    Can be used to implement a custom cleanup policy, e.g.
    check for `DOS attacks`_ or enforce a "One session per user" policy.
    Note that this event is notified in a separate thread outside
    the typical Zope request context; only very few "services"
    are available.
   

Installation
============

Unfortunately, it is more difficult to use Zope sessions
implemented by ``dm.zope.session`` than those implemented
by ``Products.Transience``. In the latter case, all you need to
do is installing ``Products.Sessions`` and (maybe) (slightly) extending
your Zope configuration file. To use ``dm.zope.session``,
you must install both it and ``Products.Sessions``, ensure that the
ZCML configuration of ``dm.zope.session`` is executed during startup
and then [re]configure Zope's session machinery via the ZMI (= "Zope
Management Interface"). To facilitate this configuration, we
sketch first Zope's session architecture.

Zope's session architecture
---------------------------

The various subtasks related to session
management are delegated to different cooperating Zope objects:

``session_data_manager``
  This objects makes the session available via the request object.
  It uses the ``browser_id_manager`` to generate a session id
  and a session container (called "transient object container")
  for the storage of the session objects.
  By default, the session container is located at
  ``/temp_folder/session_data``; this can be changed via the ZMI.

``browser_id_manager``
  This object is responsible to assign session ids (called
  browser ids, because they in fact identify the browser).

session container
  This is an object used to store (and manage) the sessions.
  Its path is determined by the ``session_data_manager``;
  by default, it is ``/temp_folder/session_data``.

``temp_folder``
  By default, this is a mount point. The mount point
  is configured in the Zope configuration file (``zope.conf``).
  Typically, it mounts a ``Products.TemporaryFolder.TemporaryContainer``
  from a ``tempstorage`` with name ``temporary``.
  A ``tempstorage`` maintains its data in RAM; therefore, the data is lost on
  restart. To (partially) counter this data loss, Zope creates (typically)
  a session container named ``session_data`` with values
  from the Zope configuration file on startup.


ZMI configuration for ``dm.zope.session``
-----------------------------------------

There are various options to configure for the use of
``dm.zope.session``.

The easiest way is to create
a ``dm.zope.session:Container`` (via the ZMI) somewhere
(but not below ``temp_folder`` where it would be lost on restart)
and then let the ``session_data_manager``'s
``Transient Object Container Path`` point to its location.
This puts the sessions into the main ZODB.

You might want to maintain the sessions in their own ZODB, e.g.
to use different parameters (such as e.g. cache size) for sessions
and the main content or use different pack parameters and/or frequencies.
To do this, you would configure a mount point in the Zope
configuration file (likely similar to the definition for the
``main`` ZODB -- do not use ``temporarystorage``!),
add a corresponding mount point in the
main ZODB (via the ZMI) and then put there the session container.

Should you use Plone, you likely would need to disable
its CSRF protection or put the session container into
a mounted ZODB with name ``temporary``: Plone's CSRF protection
looks for ZODB writes and usually allows them only, if the request
is "authenticated". To support session access (which
might cause writes even for a read access), it allows
writes to objects in ``temporary`` also for unauthenticated requests.
Likely, your Zope configuration file already contains a
definition for this ZODB, adapted for Zope's standard sessions
and based on ``temporarystorage``; you would need to replace it
by one for ``dm.zope.session`` (i.e. similar to the
definition for the ``main`` ZODB and especially not using
``temporarystorage``).


Use
===

The typical session setup (by ``Products.Sessions``)
makes the current session available as *request*\ ``["SESSION"]`` where
*request* represents the request object. The session behaves
similar to a Python ``dict``. In addition, you can use the methods
``set`` and ``delete`` to set a session "variable" or delete one, respectively.

``dm.zope.session``'s sessions are (like those
of ``Products.Transience``) ZODB based. This has
an important implication: the request does not work with
the session directly but with a local copy of the session
object maintained in the ZODB. When the request changes the
session, then in the first place it only changes the local
copy. Some changes are recognized by the ZODB --
this includes changes to the session itself and changes
to other "persistent object"s -- and cause the modifications
to update the affected persistent objects in the ZODB when
the request finishes successfully. In this case, followup requests
will see the modifications. Other changes (to non persistent objects,
e.g. lists, dicts, most class instances, ...) are
**NOT** recognized automatically and are not written to the ZODB.
In such a case, some followup requests may see the modifications
but others will not. If you use complex ("mutable") values for your
session variables, try to use "persistent objects" (the package
``persistent`` has persitent variants of lists and mappings)
or reassign a the value to the session variable after you
have changed it, e.g.::

	complex_value = session["var"]
	# modify complex_value via its methods
	session["var"] = complex_value

The code above will ensure that the change will be written
to the ZODB if the request succeeds (does not fail with an exception).


DOS attacks
===========

``dm.zope.session`` can be vulnerable to denial of service (DOS)
attacks. In such an attack, the attacker would try to force
the server to massively create new sessions. Each of those
sessions needs resources (typically file space for ``dm.zope.session``).
The attacker's aim would be to overload this kind of resource and
get the site (and maybe other services using the same resource kind)
in trouble.

``dm.zope.session`` has not enough knowledge to prevent this
kind of DOS attacks. However, it has features to limit the potential
damage and to help detecting and handling such attacks.

The simplest approach is to limit the number of sessions
by giving the configuration parameter ``session_max_number`` a positive value.
This limits resource usage. However, if you have put data
vital for the use of your site into the session, your site may still
no longer function properly because no new sessions can be created
during the attack. Therefore, try not to use the session
for the most fundamental services of your site - use cookies instead.

An alternative approach would be to try to detect and handle
attacks. ``dm.zope.session`` notifies some events to help you
with this. An ``ISessionCreatedEvent`` is notified whenever
a new session object is created. You can register a handler
to add information to the session which helps to detect and/or
handle potential attacks; potentially, the handler also performs
the detection and handling itself. An ``IMaximalSessionNumberExceededEvent``
is notified when the maximal session number would be exceeded.
In a correspoding handler, you can try to delete sessions based
on custom policies. Potentially, you try to detect a potential attack
and delete related sessions. ``dm.zope.session`` notifies
an ``ISessionCleanupEvent`` during each cleanup round. DOS
detection and handling could also be implemented in its handler;
note, however, that it runs "offline" (not inside the typical Zope
request context) and that it can use only very few Zope services.

Any attack comprises a large number of requests, all under the
control of the attacker. To detect an attack, you must
be able to recognize sessions which may have been created by the attacker.
A fairly reliable way would be to use the session only
for authenticated users (and e.g. use cookies for all services
provided for anonymous users). In this case, you could store
the corresponding user id in the session. If an attack is suspected,
you could visit all sessions, check for users with an unexpected
number of sessions and delete those, maybe even disable the user.
If you must use the session for anonymous users, you can try to
use the request's IP address in place of the user id. Note, however,
that this is far less reliable as many organisations grant internet
access only through proxies; then all organization members use
the same IP address. Therefore, it is much more difficult
to distinguish normal use from an attack. Sessions have
properties ``created`` (a timestamp float) and ``created_date`` (``DateTime``)
indicating when the session has been created;
they can help with this distinction. Note, that advanced attackers
may use a large number of (hijacked) clients; in such a case,
the attacking requests would come from different IPs; the "created" properties
might still be used to find candidates for attacker sessions - again
with reduced reliability.


Maintenance
===========

The sessions managed by ``dm.zope.session`` are typically stored
in a ``FileStorage``. Such a storage not only keeps the current
state but also historical data (important e.g. for conflict resolution,
"undo" and analysis of past events). To get rid of old, no longer
used information, you must regularly "pack" the storage.
This is particularly important for a storage hosting sessions as
sessions tend to be much more frequently changed than "normal" objects
and more frequent changes mean more irrelevant historical data.


History
=======

1.1
  * ``Session`` objects now have methods ``invalidate`` and ``isValid``
    (used by Plone)

  * ``Session`` objects referenced by events are now acquisition wrapped

  * more expressive function names for easy recognition of
    ``dm.zope.session`` transactions

  * avoid cleanups (and associated transactions) if no new sessions have
    been created
    

1.0
  Initial version

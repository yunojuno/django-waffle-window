# django-waffle-window

Django app for managing time-bound django-waffle user-flag membership.

## Background

If you have used `django-waffle` for managing feature flags, you will probably have come across the
challenge of managing which users have access to which flags at what point in time. The underlying
model allows you to assign individual users or groups to a flag, leaving you to manage how and when
to add users to a flag, or remove users from a flag. Take the following use case:

    Give access to user A to feature B for 30 days, starting Monday.

This use case can be challenging to manage at scale. Someone has to remember to turn the flag, and
then again to turn it off (which means, in practice, removing the user from the flag, or the
flag-enabled group).

This app attempts to tackle this problem by adding a `FlagMember` model that enables you to set a
date window within which a user will be added to a flag, and outside of which they will be removed.
The add / remove process is managed via management command.

```
$ python manage.py update_flag_membership
```

### Implementation

The flag membership is managed using Django Groups. For each flag, a related group called
`WAFFLE_<flag_name>` is created, and assigned to the flag. The management command then runs through
each flag, checks the `FlagMember` table for users who are assigned to the flag _on that date_, and
assigns them to the relevant group. The user membership window is defined through
`FlagMember.start_date` and `FlagMember.end_date`.

```python
class FlagMemberQuerySet(QuerySet):

    def active(flag_name: str) -> FlagMemberQuerySet:
        """Return all users assigned to the flag today."""
        on_date = datetime.date.today()
        return self.filter(
            name=flag_name,
            start_date__gte=on_date,
            end_date__lte=on_date
        )
```

Each `FlagMember` object can sync its own membership:

```python
>>> member = FlagMember(user, flag_name, start_date, end_date)
>>> member.save()  # save object, but do not add to group
>>> member.sync()  # add to / remove from group as appropriate
```

The scheduler clears the entire group and re-adds those members who are active.

```python
def _get_or_create_flag_group(flag_name: str) -> Group:
    flag = Flag.objects.get(name=flag_name)
    group = Group.objects.get_or_create(name=f"WAFFLE_{flag_name}")
    flag.group_set.add(group)
    return group

def sync_flag_membership(flag_name: str) -> None:
    """Update the flag group with all members of the queryset."""
    active_members = FlagMember.objects.active(flag_name)
    group = _get_or_create_flag_group(flag_name)
    group.user_set.clear()
    group.add(*active_members)  # this won't scale for large querysets
```

The management command updates all Flags:

```python
class Command(BaseCommand):

    def handle(self, *args, **options):
        for flag in Flag.objects.all():
            sync_flag_membership(flag.name)

```

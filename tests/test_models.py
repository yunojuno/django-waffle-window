import pytest
from django.contrib.auth import get_user_model
from waffle.models import Flag
from waffle_window.models import FlagMember, sync_flag_membership

from .utils import today, tomorrow, yesterday


@pytest.mark.django_db
class TestFlagMember:
    def test_model__defaults(self):
        user = get_user_model().objects.create_user("Jo Bloggs")
        flag = Flag.objects.create(name="test_flag")
        member = FlagMember(user=user, flag=flag)
        assert member.flag_name == "test_flag"
        assert member.group_name == "WAFFLE_test_flag"
        assert member.group.name == "WAFFLE_test_flag"
        assert member.start_date is None
        assert member.end_date is None
        assert member.is_active is None
        assert member.created_at is None

    @pytest.mark.parametrize(
        "start_date, end_date, is_active",
        (
            (None, None, None),
            (yesterday(), None, None),
            (None, tomorrow(), None),
            (yesterday(), today(), True),
            (yesterday(), tomorrow(), True),
            (today(), tomorrow(), True),
            (yesterday(), yesterday(), False),
            (tomorrow(), tomorrow(), False),
        ),
    )
    def test_model__dates(self, start_date, end_date, is_active):
        user = get_user_model().objects.create_user("Jo Bloggs")
        flag = Flag.objects.create(name="test_flag")
        member = FlagMember(
            user=user, flag=flag, start_date=start_date, end_date=end_date
        )
        assert member.start_date == start_date
        assert member.end_date == end_date
        assert member.is_active == is_active

    @pytest.mark.parametrize(
        "start_date, end_date, in_group",
        ((yesterday(), tomorrow(), True), (yesterday(), yesterday(), False)),
    )
    def test_model__sync(self, start_date, end_date, in_group):
        user = get_user_model().objects.create_user("Jo Bloggs")
        flag = Flag.objects.create(name="test_flag")
        member = FlagMember(
            user=user, flag=flag, start_date=start_date, end_date=end_date
        )
        member.save()
        group = member.group
        assert not group.user_set.exists()
        member.sync()
        assert group.user_set.exists() == in_group


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_date, end_date, count",
    ((yesterday(), tomorrow(), 1), (yesterday(), yesterday(), 0)),
)
def test_sync_flag_membership(start_date, end_date, count):
    user = get_user_model().objects.create_user("Jo Bloggs")
    flag = Flag.objects.create(name="test_flag")
    FlagMember.objects.create(
        user=user, flag=flag, start_date=start_date, end_date=end_date
    )
    assert sync_flag_membership(flag.name) == count

from rest_framework import generics
from .settings import REVERSION_ENABLED


if REVERSION_ENABLED:
    from nodeshot.core.base.mixins import RevisionCreate, RevisionUpdate

    class ListCreateAPIView(RevisionCreate, generics.ListCreateAPIView):
        pass

    class RetrieveUpdateAPIView(RevisionUpdate, generics.RetrieveUpdateAPIView):
        pass
else:
    class ListCreateAPIView(generics.ListCreateAPIView):
        pass

    class RetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
        pass

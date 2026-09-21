MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

PDK ?= ihp-sg13g2

ifeq ($(PDK),icsprout55)
PDK_ROOT ?= $(MAKEFILE_DIR)/icsprout55-openpdk
PDK ?= icsprout55
PDK_REPO ?= https://github.com/ckdur/icsprout55-openpdk
PDK_COMMIT ?= 9567646e86e660d3a8c9e1bd535aadf614937de9

OPTS = --pdk-root ${PDK_ROOT} --manual-pdk
endif

# Get the fabric names
FABRICS :=  $(patsubst fabrics/%,%,$(wildcard fabrics/*)) 

FABRICS_OPENROAD := $(addsuffix -openroad,$(FABRICS))
FABRICS_KLAYOUT := $(addsuffix -klayout,$(FABRICS))

all: $(FABRICS)
.PHONY: all

clone-icsprout55:
	mkdir -p $(PDK_ROOT)
	git clone $(PDK_REPO) --recurse-submodules --depth=1 --revision $(PDK_COMMIT) $(PDK_ROOT)
	cd $(PDK_ROOT); bash ./install.sh
.PHONY: clone-icsprout55

$(FABRICS):
	librelane --pdk ${PDK} ${OPTS} fabrics/$@/config.yaml --save-views-to fabrics/$@/macro/${PDK}/
.PHONY: $(FABRICS)

$(FABRICS_OPENROAD):
	librelane --pdk ${PDK} ${OPTS} fabrics/$(subst -openroad,,$@)/config.yaml --last-run --flow OpenInOpenROAD
.PHONY: $(FABRICS_OPENROAD)

$(FABRICS_KLAYOUT):
	librelane --pdk ${PDK} ${OPTS} fabrics/$(subst -klayout,,$@)/config.yaml --last-run --flow OpenInKLayout
.PHONY: $(FABRICS_KLAYOUT)

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

PDK ?= ihp-sg13g2

ifeq ($(PDK),ihp-sg13cmos5l)
PDK_ROOT ?= $(MAKEFILE_DIR)/IHP-Open-PDK
PDK ?= ihp-sg13cmos5l

PDK_REPO_IHP ?= https://github.com/IHP-GmbH/IHP-Open-PDK
PDK_COMMIT_IHP ?= 22f2a25f1734796de3debbbf29cf697cbbc54081

PDK_REPO ?= https://github.com/IHP-GmbH/ihp-sg13cmos5l
PDK_COMMIT ?= e8a87d708b8977e7c07684b033658a0f80af59a0

OPTS = --pdk-root ${PDK_ROOT} --manual-pdk
endif

# Get the fabric names
FABRICS :=  $(patsubst fabrics/%/config.yaml,%,$(wildcard fabrics/*/config.yaml))

FABRICS_OPENROAD := $(addsuffix -openroad,$(FABRICS))
FABRICS_KLAYOUT := $(addsuffix -klayout,$(FABRICS))

all: $(FABRICS)
.PHONY: all

clone-ihp-sg13cmos5l:
	#ciel enable $(PDK_COMMIT) --pdk-root $(PDK_ROOT) --pdk-family $(PDK)
	mkdir -p $(PDK_ROOT)
	#git clone $(PDK_REPO) --recurse-submodules --depth=1 --single-branch -b $(PDK_BRANCH) $(PDK_ROOT)
	git clone $(PDK_REPO_IHP) --recurse-submodules --depth=1 --revision $(PDK_COMMIT_IHP) $(PDK_ROOT)
	git clone $(PDK_REPO) --recurse-submodules --depth=1 --revision $(PDK_COMMIT) $(PDK_ROOT)/$(PDK)
.PHONY: clone-ihp-sg13cmos5l

$(FABRICS):
	librelane --pdk ${PDK} ${OPTS} fabrics/$@/config.yaml --save-views-to fabrics/$@/macro/${PDK}/
.PHONY: $(FABRICS)

$(FABRICS_OPENROAD):
	librelane --pdk ${PDK} ${OPTS} fabrics/$(subst -openroad,,$@)/config.yaml --last-run --flow OpenInOpenROAD
.PHONY: $(FABRICS_OPENROAD)

$(FABRICS_KLAYOUT):
	librelane --pdk ${PDK} ${OPTS} fabrics/$(subst -klayout,,$@)/config.yaml --last-run --flow OpenInKLayout
.PHONY: $(FABRICS_KLAYOUT)
